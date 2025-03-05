from dataclasses import dataclass
from enum import Enum

from breezeway.models.base import BaseBreezewayModel


class Department(Enum):
    HOUSEKEEPING = 'housekeeping'
    INSPECTION = 'inspection'
    MAINTENANCE = 'maintenance'

    @property
    def name(self) -> str:
        return {
            Department.HOUSEKEEPING: 'Cleaning',
            Department.INSPECTION: 'Inspection',
            Department.MAINTENANCE: 'Maintenance'
        }[self]


@dataclass
class Company(BaseBreezewayModel):
    id: int
    name: str
    reference_company_id: str | None = None


@dataclass
class Subdepartment(BaseBreezewayModel):
    id: int
    name: str


@dataclass
class Template(BaseBreezewayModel):
    id: int
    name: str
    department: Department

    def convert_data_types(self):
        if not isinstance(self.department, Department):
            self.department = Department(self.department)
