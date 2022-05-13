using System.Text.Json.Serialization;
using Delivery.Common;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.PipelineBehaviors;
using Delivery.Common.Queries;
using Delivery.Common.Services;
using Delivery.Common.ServicesBase;
using Delivery.Common.Settings;
using Delivery.PEK;
using Delivery.PEK.Base;
using Delivery.PEK.HttpClients;
using Delivery.PEK.Services;
using FluentValidation;
using MediatR;
using Microsoft.AspNetCore.Mvc.ApplicationParts;

var startup = new Startup();
var builder = WebApplication.CreateBuilder(args);
startup.Init(builder);

var commonAssembly = typeof(CommonAssemblyProfile).Assembly;

var applicationParts = builder.Services
    .AddControllers()
    .AddJsonOptions(opt =>
    {
        opt.JsonSerializerOptions.WriteIndented = true;
        opt.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    })
    .PartManager.ApplicationParts;
applicationParts.Add(new AssemblyPart(commonAssembly));

startup.AddServices(builder);

builder.Services.Configure<DadataSettings>(builder.Configuration.GetSection("DaData"));

builder.Services.AddAutoMapper(typeof(CommonAssemblyProfile), typeof(AutoMapperProfile));
builder.Services.AddMediatR(typeof(Program), typeof(Startup));
builder.Services.AddValidatorsFromAssemblies(new[] { typeof(Program).Assembly, typeof(Startup).Assembly });
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<GetDeliveryPricesQuery, IReadOnlyCollection<DeliveryPricingResult>>),
    typeof(AddressResolveBehavior));

builder.Services.AddSingleton<PekTownsApi>();
builder.Services.AddHttpClient<IPekTownsClient, PekTownsClient>(opt =>
{
    opt.BaseAddress = new Uri("https://www.pecom.ru");
});

builder.Services.AddSingleton<PekCalcApi>();
builder.Services.AddHttpClient<IPekCalcClient, PekCalcClient>(opt =>
{
    opt.BaseAddress = new Uri("https://calc.pecom.ru");
});

builder.Services.AddScoped<IAddressResolveService, AddressResolveService>();
builder.Services.AddScoped<IDeliveryPricingService, DeliveryPricingService>();

builder.Services.AddTransient<PekRegionResolver>();
builder.Services.AddSingleton<ITownsRepository, TownsRepository>();
builder.Services.Decorate<ITownsRepository, CachedTownsRepository>();

builder.Services.AddSingleton<IRegionsRepository, RegionsRepository>();
builder.Services.Decorate<IRegionsRepository, CachedRegionsRepository>();

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();

app.MapControllers();

app.Run();