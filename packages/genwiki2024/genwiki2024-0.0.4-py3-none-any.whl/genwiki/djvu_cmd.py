"""
Created on 2025-02-25

@author: wf
"""

import argparse
import logging
import os
import time
import traceback
from dataclasses import asdict
from typing import List

from lodstorage.lod import LOD
from ngwidgets.profiler import Profiler
from tqdm import tqdm

from genwiki.djvu_core import DjVu, DjVuFile, DjVuPage
from genwiki.djvu_manager import DjVuManager
from genwiki.djvu_processor import DjVuProcessor, ImageJob
from genwiki.tarball import Tarball


class DjVuCmd:
    """
    command line handling for djvu processing/converting
    """

    # @FIXME - remove hard coded default_base_path
    default_base_path = os.getenv(
        "GENWIKI_PATH", "/Users/wf/hd/wf-fur.bitplan.com/genwiki"
    )

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.errors = []

    @classmethod
    def get_argparser(cls) -> argparse.ArgumentParser:
        """
        Get the argument parser for the DjVu command
        """
        output_path = os.path.join(cls.default_base_path, "djvu_images")
        parser = argparse.ArgumentParser(description="Process DjVu files")  #
        parser.add_argument(
            "--base-path",
            default=cls.default_base_path,
            help="Base path for DjVu files",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of pages to process in each batch (default: 100)",
        )
        parser.add_argument(
            "--command",
            choices=["catalog", "convert", "thumbnails", "dbupdate"],
            required=True,
            help="Command to execute",
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            default=False,
            help="Enable debugging",
        )
        parser.add_argument(
            "--db-path", default="/tmp/genwiki_djvu.db", help="Path to the database"
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            default=False,
            help="Force recreation",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10000000,
            help="Maximum number of pages to process",
        )
        parser.add_argument(
            "--limit_gb",
            type=int,
            default=16,
            help="memory limit in GB [default: %(default)s]",
        )
        parser.add_argument(
            "--max-errors",
            type=float,
            default=1.0,
            help="Maximum allowed error percentage before skipping database update [default: %(default)s]",
        )
        # In get_argparser method, add this argument
        parser.add_argument(
            "--max-workers",
            type=int,
            default=None,
            help="Maximum number of worker threads (default: CPU count * 4)",
        )
        parser.add_argument(
            "--output-path", default=output_path, help="Path for PNG files"
        )
        parser.add_argument(
            "--serial",
            action="store_true",
            help="Use serial processing - parallel is default",
        )
        parser.add_argument(
            "--sort",
            choices=["asc", "desc"],
            default="asc",
            help="Sort by page count (asc=smallest first)",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=False,
            help="Enable debugging",
        )
        parser.add_argument(
            "--url", help="Process a single DjVu file (only valid in convert mode)"
        )

        return parser

    def handle_args(self):
        """
        handle the command line arguments
        """
        self.dvm = DjVuManager(db_path=self.args.db_path)
        self.dproc = DjVuProcessor(
            debug=self.args.debug,
            verbose=self.args.verbose,
            batch_size=self.args.batch_size,
            limit_gb=self.args.limit_gb,
            max_workers=self.args.max_workers,
        )
        self.profiler = Profiler(self.args.command)
        if self.args.command == "catalog":
            self.catalog_djvu()
        elif self.args.command == "convert":
            self.convert_djvu()
        elif self.args.command == "thumbnails":
            self.generate_thumbnails()
        elif self.args.command == "dbupdate":
            self.update_database()
        else:
            print(f"unknown command {self.args.command}")

    def add_page(self, page_lod, path: str, page_index: int, page):
        """
        Adds a DjVuPage to the given list of pages.

        Args:
            page_lod (list): List to which the page dictionary is appended.
            path (str): Path to the DjVu file.
            page_index (int): Index of the page.
            page: Page object containing metadata.

        Returns:
            DjVuPage: The created DjVuPage instance.
        """
        try:
            filename = page.file.name
            if "gesperrtes" in filename:
                filename = "?"
                valid = False
            else:
                valid = True
        except Exception as _ex:
            filename = "?"
            valid = False
        dpage = DjVuPage(
            # height=page.height,
            # width=page.width,
            # dpi=page.dpi,
            path=filename,
            page_index=page_index,
            valid=valid,
            djvu_path=path,
        )
        row = asdict(dpage)
        page_lod.append(row)
        return dpage

    def report_errors(self):
        """
        Reports errors collected during processing.

        - ✅ Shows ✅ (check mark) if no errors.
        - ❌ Shows ❌ (cross mark) with error count if errors occurred.
        - 📝 Lists errors if `args.debug` is enabled.
        - 📜 Shows stack traces if `args.verbose` is enabled.
        """
        if not self.errors:
            msg = " ✅ Ok"
        else:
            msg = f" ❌ {len(self.errors)} errors"
        self.profiler.time(msg)

        if self.args.debug:
            for i, error in enumerate(self.errors, 1):
                print(f"📝 {i}. {error}")

            if self.args.verbose:
                for error in self.errors:
                    print("📜", traceback.format_exc())

    def catalog_djvu(self):
        """
        First pass: Catalog DjVu files into the database
        """
        bootstrap_dvm = DjVuManager()
        lod = bootstrap_dvm.query("all_djvu")
        total = 0
        start_time = time.time()
        djvu_lod = []
        page_lod = []
        for index, r in enumerate(lod, start=1):
            path = r.get("path").replace("./", "/")
            djvu_path = self.args.base_path + path
            if not djvu_path:
                self.errors.append(Exception(f"missing {djvu_path}"))
                continue
            page_index = 0
            for document, page in self.dproc.yield_pages(djvu_path):
                page_count = len(document.pages)
                page_index += 1
                _dpage = self.add_page(page_lod, path, page_index, page)
                bundled = document.type == 2
                # if debug:
                #    print(f"    {page_index:4d}/{page_count:4d}:{filename}")
            iso_date, filesize = ImageJob.get_fileinfo(djvu_path)
            djvu = DjVu(
                path=path,
                page_count=page_count,
                bundled=bundled,
                iso_date=iso_date,
                filesize=filesize,
            )
            djvu_row = asdict(djvu)
            djvu_lod.append(djvu_row)
            total += page_index
            if total > self.args.limit:
                break
            elapsed = time.time() - start_time
            pages_per_sec = total / elapsed if elapsed > 0 else 0
            print(
                f"{index:4d} {page_count:4d} {total:7d} {pages_per_sec:7.0f} pages/s: {path}"
            )
        self.dvm.store(lod=page_lod, entity_name="Page", primary_key="page_key")
        self.dvm.store(lod=djvu_lod, entity_name="DjVu", primary_key="path")
        self.report_errors()

    def get_djvu_lod(self):
        lod = self.dvm.query("all_djvu")
        return lod

    def get_djvu_files(self, djvu_lod):
        # Handle single-file mode
        if self.args.url:
            djvu_files = [self.args.url]
        else:
            djvu_files = [r.get("path").replace("./", "/") for r in djvu_lod]
        return djvu_files

    def convert_djvu(self):
        """
        Second pass: Convert DjVu files to PNG using the database
        """
        djvu_lod = self.get_djvu_lod()
        djvu_files = self.get_djvu_files(djvu_lod)
        # select the process function parallel or serial
        process_func = (
            self.dproc.process if self.args.serial else self.dproc.process_parallel
        )
        with tqdm(total=len(djvu_files), desc="DjVu", unit="file") as pbar:
            page_count = 0
            for path in djvu_files:
                try:
                    djvu_path = self.args.base_path + path
                    djvu_file = None
                    prefix = ImageJob.get_prefix(path)
                    tar_file = os.path.join(self.args.output_path, prefix + ".tar")
                    if os.path.isfile(tar_file) and not self.args.force:
                        continue
                    for image_job in process_func(
                        djvu_path,
                        relurl=path,
                        save_png=True,
                        output_path=self.args.output_path,
                    ):
                        # collect upstream errors
                        if hasattr(image_job, "error") and image_job.error:
                            self.errors.append(image_job.error)
                            continue
                        if djvu_file is None:
                            page_count = len(image_job.document.pages)
                            djvu_file = DjVuFile(path=path, page_count=page_count)
                        image = image_job.image
                        djvu_page = DjVuPage(
                            path=image.path,
                            page_index=image.page_index,
                            valid=image.valid,
                            width=image.width,
                            height=image.height,
                            dpi=image.dpi,
                            djvu_path=image.djvu_path,
                        )
                        djvu_file.pages.append(djvu_page)
                        prefix = image_job.prefix
                        pass
                    yaml_file = os.path.join(self.dproc.output_path, prefix + ".yaml")
                    djvu_file.save_to_yaml_file(yaml_file)

                    # Ensure tarball is created after YAML is saved
                    if self.dproc.tar:
                        self.dproc.wrap_as_tarball(djvu_path)
                except BaseException as e:
                    self.errors.append(e)
                finally:
                    error_count = len(self.errors)
                    status_msg = "✅" if error_count == 0 else f"❌ {error_count}"
                    _, mem_usage = self.dproc.check_memory_usage()
                    pbar.set_postfix_str(
                        f"{mem_usage:.2f} GB {page_count} pages {status_msg}"
                    )
                    pbar.update(1)
        self.report_errors()

    def generate_thumbnails(self):
        """
        Generates thumbnails for all DjVu files.
        """
        self.errors.append(Exception("generate thumbnails not implemented yet"))
        self.report_errors()

    def get_db_records(
        self,
        tarball_file: str,
        yaml_file: str,
    ) -> List:
        page_lod = []
        yaml_data = Tarball.read_from_tar(tarball_file, yaml_file).decode("utf-8")
        djvu_file = DjVuFile.from_yaml(yaml_data)
        image_rel_dir = ImageJob.get_relative_image_path(djvu_file.path)
        image_path = os.path.join(self.args.base_path, image_rel_dir)
        for page in djvu_file.pages:
            page_record = asdict(page)
            # bundled info is not necessary available we have to
            # go by try and error
            # if not djvu_file.bundled:
            # djvu_page_path = os.path.join(image_path,page.path)
            # iso_date, filesize = ImageJob.get_fileinfo(djvu_page_path)
            # if iso_date and filesize:
            #    pass
            page_lod.append(page_record)
        return page_lod

    def update_database(self):
        """
        Updates the DjVu database.
        """
        djvu_lod = self.get_djvu_lod()
        djvu_by_path, duplicates = LOD.getLookup(djvu_lod, "path")
        if len(duplicates) > 0:
            print(f"Warning: {len(duplicates)} duplicates path enties in DjVu table")
        djvu_files = self.get_djvu_files(djvu_lod)
        error_count = 0
        page_lod = []
        with tqdm(
            total=len(djvu_files),
            desc="Updating the DjVu meta data database",
            unit="file",
        ) as pbar:
            for path in djvu_files:
                try:
                    djvu_record = djvu_by_path.get(path)
                    # djvu_path = self.args.base_path + path
                    prefix = ImageJob.get_prefix(path)
                    tar_file = os.path.join(self.args.output_path, prefix + ".tar")
                    if not os.path.isfile(tar_file):
                        raise Exception(f"tar file for {path} missing")
                    tar_iso_date, tar_filesize = ImageJob.get_fileinfo(tar_file)
                    if djvu_record:
                        djvu_record["tar_iso_date"] = tar_iso_date
                        djvu_record["tar_filesize"] = tar_filesize
                    tar_lod = self.get_db_records(tar_file, prefix + ".yaml")
                    page_lod.extend(tar_lod)
                except BaseException as e:
                    self.errors.append(e)
                finally:
                    error_count = len(self.errors)
                    status_msg = "✅" if error_count == 0 else f"❌ {error_count}"
                    pbar.set_postfix_str(status_msg)
                    pbar.update(1)
        self.report_errors()
        err_percent = error_count / len(djvu_files) * 100
        max_errors = self.args.max_errors

        # Check if the error percentage exceeds the threshold
        if err_percent > round(max_errors, 1):
            print(
                f"{err_percent:.1f}% errors ❌ > {max_errors:.1f}% limit no database update"
            )
        else:
            print(f"{err_percent:.1f}% errors ✅ < {max_errors:.1f}% limit")
            self.dvm.store(
                lod=page_lod, entity_name="Page", primary_key="page_key", with_drop=True
            )
            self.dvm.store(
                lod=djvu_lod, entity_name="DjVu", primary_key="path", with_drop=True
            )


def main():
    """
    Command-line interface for processing DjVu files and updating the database
    """
    parser = DjVuCmd.get_argparser()
    args = parser.parse_args()
    cmd = DjVuCmd(args)
    cmd.handle_args()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
