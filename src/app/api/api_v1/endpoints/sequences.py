# Copyright (C) 2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import List

from fastapi import APIRouter, Depends, Path, Security, status

from app.api.dependencies import get_jwt, get_sequence_crud
from app.crud import SequenceCRUD
from app.models import Sequence, UserRole
from app.schemas.login import TokenPayload
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the sequences")
async def fetch_sequences(
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> List[Sequence]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch")
    return [elt for elt in await sequences.fetch_all()]


@router.delete("/{sequence_id}", status_code=status.HTTP_200_OK, summary="Delete a sequence")
async def delete_sequence(
    sequence_id: int = Path(..., gt=0),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="sequence-deletion", properties={"sequence_id": sequence_id})
    await sequences.delete(sequence_id)
