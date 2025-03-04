from neurionpy.protos.neurion.ganglion.tx_pb2 import (
    MsgRegisterIon, MsgReportUnavailableIon, MsgUnreportUnavailableIon,
    MsgAddValidator, MsgRemoveValidator, MsgValidateAvailability,
    MsgRegisterPathway, MsgStakePathway, MsgRefundPathwayStake,
    MsgInitUnstakePathway, MsgClaimProtocolFee, MsgSettlePathwayStake,
    MsgStakeToGanglion, MsgClaimReward, MsgUnstakeFromGanglion,
    MsgUpdatePathway, MsgRemoveIon, MsgRemovePathway
)
from .client import get_message_client

def register_ion(capacities: list, stake: int, endpoints: list, description: str, input_schema: str, output_schema: str, fee_per_thousand_calls: int, private:bool=False,
                 allowed_pathway_owners=None) -> None:
    """Register a new Ion."""
    if allowed_pathway_owners is None:
        allowed_pathway_owners = []
    message_client = get_message_client()
    tx = message_client.RegisterIon(MsgRegisterIon(
        capacities=capacities,
        stake=stake,
        endpoints=endpoints,
        description=description,
        input_schema=input_schema,
        output_schema=output_schema,
        fee_per_thousand_calls=fee_per_thousand_calls,
        private=private,
        allowed_pathway_owners=allowed_pathway_owners
    ))
    tx.wait_to_complete()

def report_unavailable_ion(ion_address: str) -> None:
    """Report an Ion as unavailable."""
    message_client = get_message_client()
    tx = message_client.ReportUnavailableIon(MsgReportUnavailableIon(
        ion_address=ion_address
    ))
    tx.wait_to_complete()

def unreport_unavailable_ion(ion_address: str) -> None:
    """Unreport an Ion as unavailable."""
    message_client = get_message_client()
    tx = message_client.UnreportUnavailableIon(MsgUnreportUnavailableIon(
        ion_address=ion_address
    ))
    tx.wait_to_complete()

def add_validator(validator_address: str) -> None:
    """Add a new validator."""
    message_client = get_message_client()
    tx = message_client.AddValidator(MsgAddValidator(
        validator_address=validator_address
    ))
    tx.wait_to_complete()

def remove_validator(validator_address: str) -> None:
    """Remove an existing validator."""
    message_client = get_message_client()
    tx = message_client.RemoveValidator(MsgRemoveValidator(
        validator_address=validator_address
    ))
    tx.wait_to_complete()

def validate_availability(ion_address: str, available: bool) -> None:
    """Validate the availability of an Ion."""
    message_client = get_message_client()
    tx = message_client.ValidateAvailability(MsgValidateAvailability(
        ion_address=ion_address,
        available=available
    ))
    tx.wait_to_complete()

def register_pathway(name: str, description: str, is_public: bool, ions: list, field_maps_base64: list) -> None:
    """Register a new Pathway."""
    message_client = get_message_client()
    tx = message_client.RegisterPathway(MsgRegisterPathway(
        name=name,
        description=description,
        is_public=is_public,
        ions=ions,
        field_maps_base64=field_maps_base64
    ))
    tx.wait_to_complete()

def stake_pathway(pathway_id: int, amount: int) -> None:
    """Stake tokens to a Pathway."""
    message_client = get_message_client()
    tx = message_client.StakePathway(MsgStakePathway(
        id=pathway_id,
        amount=amount
    ))
    tx.wait_to_complete()

def refund_pathway_stake(pathway_id: int, user: str, num_calls: int) -> None:
    """Refund stake from a Pathway."""
    message_client = get_message_client()
    tx = message_client.RefundPathwayStake(MsgRefundPathwayStake(
        id=pathway_id,
        user=user,
        num_calls=num_calls
    ))
    tx.wait_to_complete()

def init_unstake_pathway(pathway_id: int) -> None:
    """Initiate unstaking from a Pathway."""
    message_client = get_message_client()
    tx = message_client.InitUnstakePathway(MsgInitUnstakePathway(
        id=pathway_id
    ))
    tx.wait_to_complete()

def claim_protocol_fee() -> None:
    """Claim protocol fees."""
    message_client = get_message_client()
    tx = message_client.ClaimProtocolFee(MsgClaimProtocolFee())
    tx.wait_to_complete()

def settle_pathway_stake(pathway_id: int, user: str, num_calls: int) -> None:
    """Settle stake for a Pathway."""
    message_client = get_message_client()
    tx = message_client.SettlePathwayStake(MsgSettlePathwayStake(
        id=pathway_id,
        user=user,
        num_calls=num_calls
    ))
    tx.wait_to_complete()

def stake_to_ganglion(amount: int) -> None:
    """Stake tokens to Ganglion."""
    message_client = get_message_client()
    tx = message_client.StakeToGanglion(MsgStakeToGanglion(
        amount=amount
    ))
    tx.wait_to_complete()

def claim_reward() -> None:
    """Claim rewards."""
    message_client = get_message_client()
    tx = message_client.ClaimReward(MsgClaimReward())
    tx.wait_to_complete()

def unstake_from_ganglion(amount: int) -> None:
    """Unstake tokens from Ganglion."""
    message_client = get_message_client()
    tx = message_client.UnstakeFromGanglion(MsgUnstakeFromGanglion(
        amount=amount
    ))
    tx.wait_to_complete()

def update_pathway(pathway_id: int, name: str, description: str, is_public: bool, ions: list, field_maps_base64: list) -> None:
    """Update an existing Pathway."""
    message_client = get_message_client()
    tx = message_client.UpdatePathway(MsgUpdatePathway(
        id=pathway_id,
        name=name,
        description=description,
        is_public=is_public,
        ions=ions,
        field_maps_base64=field_maps_base64
    ))
    tx.wait_to_complete()

def remove_ion() -> None:
    """Remove an Ion."""
    message_client = get_message_client()
    tx = message_client.RemoveIon(MsgRemoveIon())
    tx.wait_to_complete()

def remove_pathway() -> None:
    """Remove a pathway."""
    message_client = get_message_client()
    tx = message_client.RemovePathway(MsgRemovePathway())
    tx.wait_to_complete()