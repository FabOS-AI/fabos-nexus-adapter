from typing import Dict, List, Optional, Set

from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth

class Checksum(BaseModel):
    sha1: Optional[str]
    sha256: Optional[str]
    sha512: Optional[str]
    md5: str

    @classmethod
    def from_dict(cls, d: Dict[str, str]):
        sha1 = d.get("sha1")
        sha256 = d.get("sha256")
        sha512 = d.get("sha512")
        md5 = d["md5"]
        return cls(sha1=sha1, sha256=sha256, sha512=sha512, md5=md5)

class NexusAsset(BaseModel):
    """
    Nexus metadata for a single asset (file)
    Follows the example response above and the Nexus API documentation
    """
    downloadUrl: str
    path: str
    id: str
    repository: str
    format: str
    checksum: Checksum
    contentType: str
    lastModified: str
    lastDownloaded: Optional[str]
    uploader: str
    uploaderIp: str
    fileSize: int
    manifest_path: str = ""
    git_blame_path: str = ""

    def __repr__(self):
        return f"NexusAsset({self.path})"

    def __str__(self):
        lines = []
        lines.append(f"{self.path}")
        lines.append(f"  id: {self.id}")
        lines.append(f"  repository: {self.repository}")
        lines.append(f"  format: {self.format}")
        lines.append(f"  checksum: {self.checksum.md5}")
        lines.append(f"  contentType: {self.contentType}")
        lines.append(f"  lastModified: {self.lastModified}")
        lines.append(f"  lastDownloaded: {self.lastDownloaded}")
        lines.append(f"  uploader: {self.uploader}")
        lines.append(f"  uploaderIp: {self.uploaderIp}")
        lines.append(f"  fileSize: {self.fileSize}")
        return "\n".join(lines)


class RemoteAssets(List[NexusAsset]):
    def __init__(self, config: Dict, nexus_auth: Dict, include_metadata_files: bool = False, update_on_init: bool = True):
        super().__init__()
        self.config = config
        self.nexus_config = config
        self.username = nexus_auth.get('username')
        self.password = nexus_auth.get('password')
        self.include_metadata_files = include_metadata_files

        if update_on_init:
            self.update()

    
    def __repr__(self):
        return f"RemoteAssets({len(self)} assets)"

    def __str__(self):
        return self.__repr__()

    def update(self):
        self.clear()
        self.extend(self._get_nexus_assets())

    def _get_nexus_assets(self, name: Optional[str] = None) -> List[NexusAsset]:
        """
        Call nexus rest api to get all assets
        """

        search_url = self.nexus_config['search_url']
        if name is not None:
            search_url = f"{search_url}&name={name}"

        items = []
        continuationToken = None
        while True:
            if continuationToken is not None:
                url = f"{search_url}&continuationToken={continuationToken}"
            else:
                url = search_url

            # r = self.http.get(url, auth=(self.username, self.password), timeout=5)
            r = requests.get(url=url, auth=HTTPBasicAuth(self.username, self.password))
            # check status code
            if r.status_code == 401:
                raise Exception(f"Failed to get nexus assets. Status code: {r.status_code}. Wrong username or password? Response body: {r.text}")
            if r.status_code != 200:
                raise Exception(f"Failed to get nexus assets. Status code: {r.status_code}. Response body: {r.text}")
            data = r.json()
            items += data["items"]
            continuationToken = data.get("continuationToken", None)
            if continuationToken is None:
                break
            self.config.verbose_echo(f"Continuation token: {continuationToken}")
        

        existing_assets = []
        git_meta_set: Set[str] = set()
        manifest_meta_set: Set[str] = set()
        for item in items:
            # check if it is a metadata file
            if item["path"].endswith(".git-blame.json"):
                git_meta_set.add(item["path"])
                continue
            if item["path"].endswith(".manifest.toml"):
                manifest_meta_set.add(item["path"])
                continue

            # parse checksum
            item["checksum"] = Checksum.from_dict(item["checksum"])
            existing_assets.append(NexusAsset(**item))
        
        for asset in existing_assets:
            if asset.path + ".git-blame.json" in git_meta_set:
                asset.git_blame_path = asset.path
            if asset.path + ".manifest.toml" in manifest_meta_set:
                asset.manifest_path = asset.path

        existing_assets = sorted(existing_assets, key=lambda x: ('/' not in x.path, x.path))

        return existing_assets