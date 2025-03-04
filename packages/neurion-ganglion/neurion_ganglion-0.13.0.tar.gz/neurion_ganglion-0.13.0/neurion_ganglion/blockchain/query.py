from neurionpy.protos.neurion.ganglion.query_pb2 import (
    QueryParamsRequest, QueryParamsResponse,
    QueryIonByIonAddressRequest, QueryIonByIonAddressResponse,
    QueryIonByCreatorRequest, QueryIonByCreatorResponse,
    QueryIonsByInputSchemaHashRequest, QueryIonsByInputSchemaHashResponse,
    QueryGetPathwayRequest, QueryGetPathwayResponse,
    QueryListPathwaysRequest, QueryListPathwaysResponse,
    QueryListIonsByAddressesRequest, QueryListIonsByAddressesResponse,
    QueryUserPathwayStakeRequest, QueryUserPathwayStakeResponse,
    QueryGetUserRewardRequest, QueryGetUserRewardResponse,
    QueryGetProtocolFeeRequest, QueryGetProtocolFeeResponse,
    QueryPathwaysUsingIonRequest, QueryPathwaysUsingIonResponse,
    QueryIonsByReportsRequest, QueryIonsByReportsResponse,
    QueryListAllPathwaysRequest, QueryListAllPathwaysResponse,
    QueryGetRewardRequest, QueryGetRewardResponse,
    QueryGetStakeRequest, QueryGetStakeResponse,
    QueryGetIonRequest, QueryGetIonResponse,
    QueryGetPathwayUnstakeInitiatedUsersRequest, QueryGetPathwayUnstakeInitiatedUsersResponse,
    QueryGetAvailableIonsRequest, QueryGetAvailableIonsResponse,
    QueryGetAllowedIpsRequest, QueryGetAllowedIpsResponse
)
from .client import get_query_client
from .wallet import get_wallet

def params() -> QueryParamsResponse:
    """Query module parameters."""
    query_client = get_query_client()
    return query_client.Params(QueryParamsRequest())

def ion_by_ion_address(ion_address: str) -> QueryIonByIonAddressResponse:
    """Query an Ion by its ion_address."""
    query_client = get_query_client()
    return query_client.IonByIonAddress(QueryIonByIonAddressRequest(ion_address=ion_address))

def ion_by_creator() -> QueryIonByCreatorResponse:
    """Query an Ion by its creator."""
    query_client = get_query_client()
    wallet = get_wallet()
    return query_client.IonByCreator(QueryIonByCreatorRequest(creator=str(wallet.address())))

def ions_by_input_schema_hash(input_schema_hash: str, user:str,offset: int, limit: int) -> QueryIonsByInputSchemaHashResponse:
    """Query Ions by input_schema_hash with pagination."""
    query_client = get_query_client()
    return query_client.IonsByInputSchemaHash(QueryIonsByInputSchemaHashRequest(
        input_schema_hash=input_schema_hash, user=user, offset=offset, limit=limit
    ))

def get_pathway(pathway_id: int) -> QueryGetPathwayResponse:
    """Query a pathway by its ID."""
    query_client = get_query_client()
    return query_client.GetPathway(QueryGetPathwayRequest(id=pathway_id))

def list_pathways(offset: int, limit: int) -> QueryListPathwaysResponse:
    """List pathways for a creator with pagination."""
    query_client = get_query_client()
    wallet = get_wallet()
    return query_client.ListPathways(QueryListPathwaysRequest(creator=str(wallet.address()), offset=offset, limit=limit))

def list_ions_by_addresses(ion_addresses: list) -> QueryListIonsByAddressesResponse:
    """List Ions by a list of ion addresses."""
    query_client = get_query_client()
    return query_client.ListIonsByAddresses(QueryListIonsByAddressesRequest(ion_addresses=ion_addresses))

def user_pathway_stake(user:str,pathway_id: int) -> QueryUserPathwayStakeResponse:
    """Query pathway stake for a given pathway and user."""
    query_client = get_query_client()
    return query_client.UserPathwayStake(QueryUserPathwayStakeRequest(id=pathway_id, user=user))

def get_protocol_fee() -> QueryGetProtocolFeeResponse:
    """Query the protocol fee."""
    query_client = get_query_client()
    return query_client.GetProtocolFee(QueryGetProtocolFeeRequest())

def pathways_using_ion(ion_address: str) -> QueryPathwaysUsingIonResponse:
    """Query pathways using a given ion."""
    query_client = get_query_client()
    return query_client.PathwaysUsingIon(QueryPathwaysUsingIonRequest(ion_address=ion_address))

def ions_by_reports(offset: int, limit: int) -> QueryIonsByReportsResponse:
    """Query ions by reports with pagination."""
    query_client = get_query_client()
    return query_client.IonsByReports(QueryIonsByReportsRequest(offset=offset, limit=limit))

def list_all_pathways(offset: int, limit: int) -> QueryListAllPathwaysResponse:
    """List all pathways with pagination."""
    query_client = get_query_client()
    return query_client.ListAllPathways(QueryListAllPathwaysRequest(offset=offset, limit=limit))

def get_stake() -> QueryGetStakeResponse:
    """Query stake for a given user."""
    query_client = get_query_client()
    wallet = get_wallet()
    return query_client.GetStake(QueryGetStakeRequest(user=str(wallet.address())))

def get_fee_reward() -> QueryGetUserRewardResponse:
    """Query user reward."""
    query_client = get_query_client()
    wallet = get_wallet()
    return query_client.GetUserReward(QueryGetUserRewardRequest(user=str(wallet.address())))

def get_stake_reward() -> QueryGetRewardResponse:
    """Query reward for a given user."""
    query_client = get_query_client()
    wallet = get_wallet()
    return query_client.GetReward(QueryGetRewardRequest(user=str(wallet.address())))

def get_ion(ion_id: int) -> QueryGetIonResponse:
    """Query an Ion by its ID."""
    query_client = get_query_client()
    return query_client.GetIon(QueryGetIonRequest(id=ion_id))

def get_pathway_unstake_initiated_users() -> QueryGetPathwayUnstakeInitiatedUsersResponse:
    """Query pathway unstake initiated users."""
    query_client = get_query_client()
    return query_client.GetPathwayUnstakeInitiatedUsers(QueryGetPathwayUnstakeInitiatedUsersRequest())

def get_available_ions(user:str, offset: int, limit: int) -> QueryGetAvailableIonsResponse:
    """Query available Ions with pagination."""
    query_client = get_query_client()
    return query_client.GetAvailableIons(QueryGetAvailableIonsRequest(user=user,offset=offset, limit=limit))

def get_allowed_ips() -> QueryGetAllowedIpsResponse:
    """Query allowed IPs."""
    query_client = get_query_client()
    return query_client.GetAllowedIps(QueryGetAllowedIpsRequest())