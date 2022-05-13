using FluentValidation.Results;

namespace Delivery.Common.Exceptions;

public class ValidationException : System.Exception
{
    public ValidationException(string message, System.Exception innerException = null) : base(message, innerException)
    {
    }

    public ValidationException(ICollection<ValidationFailure> failures)
        : base(string.Join("; ", failures), null)
    {
    }
}