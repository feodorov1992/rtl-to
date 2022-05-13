using System.Text.Json.Serialization;
using Delivery.Common;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.PipelineBehaviors;
using Delivery.Common.Queries;
using Delivery.Common.Services;
using Delivery.Common.ServicesBase;
using Delivery.Common.Settings;
using Delivery.SDEK;
using Delivery.SDEK.Base;
using Delivery.SDEK.HttpClients;
using Delivery.SDEK.Services;
using Delivery.SDEK.Settings;
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

builder.Services.Configure<ApiSettings>(builder.Configuration.GetSection("SDEK"));
builder.Services.Configure<DadataSettings>(builder.Configuration.GetSection("DaData"));

builder.Services.AddAutoMapper(typeof(CommonAssemblyProfile), typeof(AutoMapperProfile));
builder.Services.AddMediatR(typeof(Program), typeof(Startup));
builder.Services.AddValidatorsFromAssemblies(new[] { typeof(Program).Assembly, typeof(Startup).Assembly });
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<GetDeliveryPricesQuery, IReadOnlyCollection<DeliveryPricingResult>>),
    typeof(AddressResolveBehavior));

builder.Services.AddSingleton<SdekApi>();
builder.Services.AddHttpClient<ISdekClient, SdekClient>(opt =>
{
    opt.BaseAddress = builder.Configuration.GetValue<Uri>("SDEK:BaseUrl");
});

builder.Services.AddScoped<IAddressResolveService, AddressResolveService>();
builder.Services.AddScoped<IDeliveryPricingService, DeliveryPricingService>();

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();

app.MapControllers();

app.Run();