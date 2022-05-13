using AutoMapper;
using Delivery.Common.Requests;
using Delivery.ZDE.Models;

namespace Delivery.ZDE;

public class AutoMapperProfile : Profile
{
    public AutoMapperProfile()
    {
        CreateMap<DeliveryPricingRequest, PriceAddressRequestModel>()
            .ForMember(x => x.From, opt => opt.MapFrom(src => src.FromAddress))
            .ForMember(x => x.To, opt => opt.MapFrom(src => src.ToAddress))
            .ForMember(x => x.Type, opt => opt.MapFrom(_ => 1))
            .ForMember(x => x.Width, opt => opt.MapFrom(src => src.Width / 100))
            .ForMember(x => x.Length, opt => opt.MapFrom(src => src.Length / 100))
            .ForMember(x => x.Height, opt => opt.MapFrom(src => src.Height / 100))
            .ForMember(x => x.Services,  opt => opt.MapFrom(src => 
                src.ExtraServices != null ? string.Join(",", new HashSet<string>(src.ExtraServices)) : null));
    }
}