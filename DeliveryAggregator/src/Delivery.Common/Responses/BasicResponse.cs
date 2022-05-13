using Newtonsoft.Json;

namespace Delivery.Common.Responses;

public record BasicResponse<T>
{
    public T Data { get; init; }
    
    public string Error { get; init; }
    
    public string Details { get; init; }
    
    public ResponseStatus Result { get; init; }

    public static BasicResponse<T> Success(T data)
    {
        return new BasicResponse<T>
        {
            Data = data,
            Result = ResponseStatus.Success,
            Error = null
        };
    }

    public static BasicResponse<T> Fail(string error, string details)
    {
        return new BasicResponse<T>
        {
            Data = default,
            Result = ResponseStatus.Error,
            Error = error,
            Details = details
        };
    }
}