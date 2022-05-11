using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Queries;
using Delivery.Common.ServicesBase;
using MediatR;
using Serilog;

namespace Delivery.Common.PipelineBehaviors;

public class AddressResolveBehavior : IPipelineBehavior<GetDeliveryPricesQuery, IReadOnlyCollection<DeliveryPricingResult>>
{
    private readonly IAddressResolveService _addressResolveService;

    public AddressResolveBehavior(IAddressResolveService addressResolveService)
    {
        _addressResolveService = addressResolveService;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> Handle(GetDeliveryPricesQuery request, 
        CancellationToken cancellationToken, 
        RequestHandlerDelegate<IReadOnlyCollection<DeliveryPricingResult>> next)
    {
        Log.Information("Got {query_name}. Attempting to resolve address through DaData", nameof(GetDeliveryPricesQuery));

        AddressShortModel resolvedFromAddress = null;
        AddressShortModel resolvedToAddress = null;
        
        try
        {
            resolvedFromAddress = await _addressResolveService.Resolve(request.Request.FromAddress);
            Log.Information("Successfully resolved address {original} to {resolved}", request.Request.FromAddress,
                resolvedFromAddress.FormattedAddress);
        }
        catch (Exception e)
        {
            Log.Error(e, "Failed to resolve 'from' address of value: {from_address}", request.Request.FromAddress);
        }
        
        try
        {
            resolvedToAddress = await _addressResolveService.Resolve(request.Request.ToAddress);
            Log.Information("Successfully resolved address {original} to {resolved}", request.Request.ToAddress,
                resolvedToAddress.FormattedAddress);
        }
        catch (Exception e)
        {
            Log.Error(e, "Failed to resolve 'to' address of value: {to_address}", request.Request.ToAddress);
        }
        
        request.AddFormattedAddresses(resolvedFromAddress, resolvedToAddress);
        
        return await next();
    }
}