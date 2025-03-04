import requests
import os
import random

from typing import Dict, Optional, Union
from pydantic import BaseModel, Field

def random_char(y: int) -> str:
    """
    Generates a random str of "y" chars
    """
    return "".join(chr(random.randrange(97, 97 + 26)) for x in range(y))

class SidpHemeraOptions(BaseModel):
    ai_gen_assistant: bool = Field(
        default=False, description="Enable AI generation assistant"
    )
    install_mssql: bool = Field(
        default=False, description="Install Microsoft SQL Server"
    )
    install_oracle: bool = Field(default=False, description="Install Oracle Database")
    install_mariadb: bool = Field(default=False, description="Install MariaDB")
    install_psql: bool = Field(default=False, description="Install PostgreSQL")
    trusted_ips: str = Field(default="0.0.0.0/0", description="Whitelisted IP adresses")

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the model to a dictionary representation.

        :return: Dictionary of Hemera options
        """
        return {
            "ai_gen_assistant": self.ai_gen_assistant,
            "install_mssql": self.install_mssql,
            "install_oracle": self.install_oracle,
            "install_mariadb": self.install_mariadb,
            "install_psql": self.install_psql,
            "trusted_ips": self.trusted_ips,
        }

class SidpExtraOptions(BaseModel):
    provision: bool = Field(
        default=False, description="Provision cluster with dummy data"
    )
    provisioning_job: str = Field(
        default="init_dataplatform", description="Select provisioning data set"
    )
    no_hemera_deploy: bool = Field(
        default=False, description="Whether to install Hemera or not"
    )

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the model to a dictionary representation.

        :return: Dictionary of Extra options
        """
        return {
            "provision": self.provision,
            "no_hemera_deploy": self.no_hemera_deploy,
            "provisioning_job": self.provisioning_job,
        }

class SidpConfigurator(BaseModel):
    clusterName: str = Field(default="", description="Name of the cluster")
    kubeVersion: Optional[str] = Field(default=None, description="Kubernetes version")
    sourceBranch: Optional[str] = Field(default=None, description="Source branch")
    clusterOwner: Optional[str] = Field(default=None, description="Owner of the resource")
    hemeraOptions: SidpHemeraOptions = Field(
        default_factory=SidpHemeraOptions, description="Hemera-specific options"
    )
    extraOptions: SidpExtraOptions = Field(
        default_factory=SidpExtraOptions, description="Additional configuration options"
    )

    def validate(self) -> bool:
        """
        Validate the configurator.

        :return: True if valid, False otherwise
        """
        return bool(self.clusterName)

class SIDPClient:
    def __init__(self, base_url: str, config: SidpConfigurator):
        """
        Initialize the SIDP API Client

        :param base_url: Base URL of the SIDP API (e.g., 'http://localhost:3000')
        """
        self.base_url = base_url.rstrip("/")
        self._config = config

        if os.environ.get("SIDP_API_ENDPOINT_USERNAME") and os.environ.get(
            "SIDP_API_ENDPOINT_PASSWORD"
        ):
            self.auth = requests.auth.HTTPBasicAuth(
                os.environ.get("SIDP_API_ENDPOINT_USERNAME"),
                os.environ.get("SIDP_API_ENDPOINT_PASSWORD"),
            )
        else:
            self.auth = None

    def create_cluster(self) -> Dict[str, Union[str, int]]:
        """
        Create a new cluster using a SidpConfigurator

        :return: Dictionary with command output and task_id
        """
        response = requests.post(
            f"{self.base_url}/api/create", json=self._config.model_dump(),auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, str]:
        """
        Check the status of a task

        :return: Dictionary with command output
        """
        response = requests.get(f"{self.base_url}/api/task_status/{task_id}",auth=self.auth)
        response.raise_for_status()
        return response.json()

    def delete_cluster(self) -> Dict[str, str]:
        """
        Delete a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/delete", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_cluster_info(self) -> Dict[str, Union[str, Dict]]:
        """
        Get information about a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/info", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_kubeconfig(self) -> Dict[str, str]:
        """
        Retrieve kubeconfig for a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/get-kubeconf", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def resume_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        Resume a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/resume", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def pause_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        Pause a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/pause", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def list_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        List all clusters

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/list", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    def list_tags(self) -> Dict[str, Union[str, Dict]]:
        """
        List Hemera tags

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(f"{self.base_url}/api/list-tags", json=payload,auth=self.auth)
        response.raise_for_status()
        return response.json()

    @property
    def config(self) -> SidpConfigurator:
        """
        Output current SidpConfigurator object

        :return: Dictionary with kubeconfig contents
        """
        return self._config
