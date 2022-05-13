namespace Delivery.Common.Exceptions;

public static class ExceptionKey
{
    public const string UNAUTHORIZED_ACCESS = "Unauthorized_Access";
    public const string SERVICE_BUSY = "Service_Busy";
    public const string SERVER_ERROR_OCCURED = "A_Server_Error_Occurred";
    public const string INVALID_ENTRY = "Invalid_Entry";
    public const string REQUEST_VALIDATION_FAILURE = "Request_Validation_Failure";
    public const string ENTITY_NOT_FOUND = "Entity_Not_Found";
    public const string INFRASTRUCTURE_ERROR = "Infrastructure_Error";
    public const string INTERNAL_SERVER_ERROR = "InternalServerError (report to a program administrator)";
    public const string METHOD_NOT_IMPLEMENTED = "Method_Is_Not_Implemented";
}