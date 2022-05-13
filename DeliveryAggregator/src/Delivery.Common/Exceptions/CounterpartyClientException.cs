namespace Delivery.Common.Exceptions;

public class CounterpartyClientException : Exception
{
    public string Error { get; }

    public CounterpartyClientException(string error, Exception innerException = null)
     : base($"Counterparty client error: {error}", innerException)
    {
        Error = error;
    }
}