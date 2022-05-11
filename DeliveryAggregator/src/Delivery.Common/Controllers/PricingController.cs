using AutoMapper;
using Delivery.Common.Queries;
using Delivery.Common.Requests;
using Delivery.Common.Responses;
using Delivery.Common.Responses.DeliveryPricing;
using Delivery.Common.ServicesBase;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace Delivery.Common.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PricingController
{
    private readonly IMediator _mediator;
    private readonly IMapper _mapper;

    public PricingController(IMediator mediator, IMapper mapper)
    {
        _mediator = mediator;
        _mapper = mapper;
    }
    
    [HttpGet]
    public async Task<ActionResult<BasicResponse<IReadOnlyCollection<DeliveryPricingResponse>>>> GetPrice([FromQuery] DeliveryPricingRequest request)
    {
        var result = await _mediator.Send(new GetDeliveryPricesQuery(request));
        var response = _mapper.Map<List<DeliveryPricingResponse>>(result);
        return BasicResponse<IReadOnlyCollection<DeliveryPricingResponse>>.Success(response);
    }
}