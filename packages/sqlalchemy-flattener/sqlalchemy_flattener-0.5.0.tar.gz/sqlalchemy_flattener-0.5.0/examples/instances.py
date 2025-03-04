from datetime import datetime
from uuid import UUID

from .models import (
    AccountType,
    Address,
    BankDetails,
    Category,
    Contact,
    Supplier,
    SupplierTag,
)

nested_supplier = Supplier(
    id=UUID("2b7e7211-d2c7-4eb4-8c14-05ed58c77473"),
    name="Loros Grist",
    email="info@loros.example",
    tags=[SupplierTag.CHEAP, SupplierTag.RELIABLE],
    created_at=datetime(2020, 2, 21),
    address_id=UUID("c5fb851f-63fd-4572-872c-3597186c9afe"),
    bank_details_id=UUID("ccd390cf-a74c-4897-a923-3d77ce1b97bf"),
    address=Address(
        id=UUID("c5fb851f-63fd-4572-872c-3597186c9afe"),
        line_1="Celestia",
    ),
    bank_details=BankDetails(
        id=UUID("ccd390cf-a74c-4897-a923-3d77ce1b97bf"),
        account_number="payusnothing",
        account_type=AccountType.CASH,
    ),
    categories=[
        Category(
            id=UUID("3674c73c-a967-493f-9a4b-5b70f78a5a99"),
            name="Baked goods",
        ),
        Category(
            id=UUID("f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"),
            name="ISP",
        ),
    ],
    contacts=[
        Contact(
            id=UUID("98a11210-949a-48ad-99c7-1d89c54c2a53"),
            name="Sveimann Glort",
            email="sveimann@loros.example",
            address_id=UUID("cd521f7e-df61-4079-b44d-35015b9b5110"),
            supplier_id=UUID("2b7e7211-d2c7-4eb4-8c14-05ed58c77473"),
            address=Address(
                id=UUID("cd521f7e-df61-4079-b44d-35015b9b5110"),
                line_1="The imperial road",
            ),
        ),
    ],
)
