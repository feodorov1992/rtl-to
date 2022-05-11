using MediatR;
using Serilog;

namespace Delivery.Common.PipelineBehaviors;

public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    public Task<TResponse> Handle(TRequest request, CancellationToken cancellationToken, RequestHandlerDelegate<TResponse> next)
    {
        Log.Information("Started executing {request}", request.GetType().Name);
        
        var response = next();
        
        Log.Information("Execution for {request} complete", request.GetType().Name);

        return response;
    }
}