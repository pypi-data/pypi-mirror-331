"""Class for generating unique identifiers for biological entities."""

import logging
import os
import pathlib
import time
import uuid
import yaml


from typing import Optional
from singleton_decorator import singleton

from kis_uid_generator_utils import constants


DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP,
)


@singleton
class Generator:
    """Class for generating unique identifiers for biological entities."""

    def __init__(self, **kwargs):
        """Constructor for class Generator"""
        self.bionamespace = kwargs.get("bionamespace", None)
        self.config = kwargs.get("config", None)
        self.config_file = kwargs.get("config_file", None)
        self.logfile = kwargs.get("logfile", None)
        self.outdir = kwargs.get("outdir", DEFAULT_OUTDIR)
        self.organization = kwargs.get("organization", None)
        self.verbose = kwargs.get("verbose", constants.DEFAULT_VERBOSE)

        self._last_timestamp = 0
        self._sequence = 0

        if self.config is None:

            logging.info(f"Will load contents of config file '{self.config_file}'")
            self.config = yaml.safe_load(pathlib.Path(self.config_file).read_text())

        if self.organization is None:
            self.organization = self.config.get(
                "organization", constants.DEFAULT_ORGANIZATION
            )
            logging.info(
                f"organization was not defined and therefore was set to default value '{self.organization}'"
            )

        if self.bionamespace is None:
            # Namespace for biological entities
            self.bionamespace = uuid.uuid5(uuid.NAMESPACE_DNS, self.organization)

        self.entity_prefixes = self.config.get("entity_prefixes", None)
        if self.entity_prefixes is None:
            raise ValueError(
                "entity_prefixes must be defined in the configuration file"
            )

        logging.info(f"Instantiated Generator in {os.path.abspath(__file__)}")

    def generate_id(self, entity_type: str, custom_name: Optional[str] = None) -> str:
        """Generate a unique identifier for a biological entity.

        Args:
            entity_type: Type of biological entity (gene, protein, etc.)
            custom_name: Optional custom name to include in the ID

        Returns:
            A unique identifier string (e.g., "GN-BRCA1-5f8b3a2e-20250304")

        Raises:
            ValueError: If entity_type is not recognized
        """
        if entity_type.lower() not in self.entity_prefixes:
            raise ValueError(
                f"Unknown entity type. Must be one of: {', '.join(self.entity_prefixes.keys())}"
            )

        prefix = self.entity_prefixes[entity_type.lower()]

        # Get current timestamp
        current_time = int(time.time())

        # Ensure monotonicity in case of multiple calls in the same second
        if current_time == self._last_timestamp:
            self._sequence += 1
        else:
            self._sequence = 0
            self._last_timestamp = current_time

        # Generate UUID based on timestamp and entity type
        base_string = f"{entity_type}{current_time}{self._sequence}"
        if custom_name:
            base_string += custom_name

        unique_id = uuid.uuid5(self.bionamespace, base_string)

        # Format the date portion
        date_str = time.strftime("%Y%m%d", time.localtime(current_time))

        # Combine prefix, custom_name (if provided), UUID hex (shortened), and date
        if custom_name:
            return f"{prefix}-{custom_name}-{unique_id.hex[:8]}-{date_str}"
        return f"{prefix}-{unique_id.hex[:8]}-{date_str}"
