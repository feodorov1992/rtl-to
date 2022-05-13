using AutoMapper;
using Dadata;
using Dadata.Model;
using Delivery.Common.Models.AddressResolve;
using Delivery.Common.ServicesBase;
using Delivery.Common.Settings;
using Microsoft.Extensions.Options;

namespace Delivery.Common.Services;

public class AddressResolveService : IAddressResolveService
{
    private readonly IMapper _mapper;
    private readonly DadataSettings _settings;

    public AddressResolveService(IOptions<DadataSettings> settings, IMapper mapper)
    {
        _mapper = mapper;
        _settings = settings.Value;
    }

    public async Task<AddressShortModel> Resolve(string address)
    {
        var api = new CleanClientAsync(_settings.Token, _settings.Secret);
        var resolvedAddress = await api.Clean<Address>(address);
        return _mapper.Map<AddressShortModel>(resolvedAddress);
    }
}