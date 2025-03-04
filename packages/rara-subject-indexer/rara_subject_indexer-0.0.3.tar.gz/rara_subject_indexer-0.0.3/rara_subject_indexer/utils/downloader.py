import os
import re
import logging
import requests
import zipfile

logger = logging.getLogger(__name__)


class Downloader:
    """
    Downloads pretrained models and other relevant data from Google Drive.

    The downloader accepts a shareable Google Drive URL or file ID.
    If the downloaded file is a zip archive, it will be extracted.
    """
    BASE_URL = "https://docs.google.com/uc?export=download"

    def __init__(
        self,
        drive_url: str,
        output_dir: str = os.path.join(os.path.expanduser("~"), "rara_subject_indexer_resources")
    ):
        """
        Parameters
        ----------
        drive_url : str
            Google Drive shareable URL or file ID.
        output_dir : str, optional
            Directory to save downloaded data, by default "downloaded_models"
        """
        self.drive_url = drive_url
        self.output_dir = output_dir

    def download(self) -> None:
        """
        Download the file from Google Drive.
        The downloader extracts the file ID from the URL if needed and downloads the file.
        If the file is a zip archive, it is automatically extracted.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        file_id = self._extract_file_id(self.drive_url)
        if not file_id:
            raise ValueError("Could not extract file id from the provided URL.")

        destination = os.path.join(self.output_dir, f"{file_id}.download")
        logger.info(f"Downloading file {file_id} to {destination}")

        self.download_file_from_google_drive(file_id, destination)

        if destination.endswith('.zip') or self._is_zip_file(destination):
            logger.info("Zip archive detected, extracting...")
            try:
                with zipfile.ZipFile(destination, 'r') as zip_ref:
                    zip_ref.extractall(self.output_dir)
                logger.info(f"Extracted zip archive to {self.output_dir}")
            except Exception as e:
                logger.error(f"Failed to extract zip archive: {e}")
                raise e
            os.remove(destination)

    def _extract_file_id(self, url: str) -> str:
        """
        Extract the file id from a Google Drive shareable URL.

        Parameters
        ----------
        url : str
            Google Drive URL or file id.

        Returns
        -------
        str
            The file id.
        """
        # If the url already looks like a file id (i.e. no slashes), return it.
        if "/" not in url:
            return url

        # Match file id patterns: e.g., /d/<file_id>/ or ?id=<file_id>
        patterns = [
            r"/d/([a-zA-Z0-9_-]+)",  # common drive url format
            r"id=([a-zA-Z0-9_-]+)"  # query parameter format
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def download_file_from_google_drive(self, file_id: str, destination: str) -> None:
        """
        Download a file from Google Drive given a file id.

        Parameters
        ----------
        file_id : str
            The Google Drive file id.
        destination : str
            Path to save the downloaded file.
        """
        session = requests.Session()
        # Always include confirm=1 as a workaround for large files.
        params = {"id": file_id, "confirm": 1}
        response = session.get(self.BASE_URL, params=params, stream=True)
        self._save_response_content(response, destination)
        logger.info(f"Downloaded file saved to {destination}")

    def _save_response_content(self, response: requests.Response, destination: str) -> None:
        """
        Save the content of a response to disk in chunks.

        Parameters
        ----------
        response : requests.Response
            The HTTP response from the download request.
        destination : str
            Path to save the downloaded file.
        """
        CHUNK_SIZE = 32768
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    def _is_zip_file(self, file_path: str) -> bool:
        """
        Check whether the given file is a zip archive.

        Parameters
        ----------
        file_path : str
            Path to the file.

        Returns
        -------
        bool
            True if the file is a zip archive, False otherwise.
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                _ = zip_ref.namelist()
            return True
        except zipfile.BadZipFile:
            return False