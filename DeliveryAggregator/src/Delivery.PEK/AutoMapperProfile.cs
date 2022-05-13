using AutoMapper;
using Delivery.Common.Requests;
using Delivery.PEK.Models;

namespace Delivery.PEK;

public class AutoMapperProfile : Profile
{
    public AutoMapperProfile()
    {
        CreateMap<DeliveryPricingRequest, PriceDeliveryRequestModel>()
            .ForMember(x => x.Width, opt => opt.MapFrom(src => src.Width / 100))
            .ForMember(x => x.Length, opt => opt.MapFrom(src => src.Length / 100))
            .ForMember(x => x.Height, opt => opt.MapFrom(src => src.Height / 100));
    }
}