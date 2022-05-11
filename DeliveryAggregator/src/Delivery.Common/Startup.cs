using System.Reflection;
using Delivery.Common.Filters;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Serialization;
using Serilog;

namespace Delivery.Common;

public class Startup
{
    public void Init(WebApplicationBuilder builder)
    {
        builder.Host.ConfigureAppConfiguration((_, config) =>
        {
            config.AddKeyPerFile("/run/secrets", optional: true);
            config.AddUserSecrets(Assembly.GetExecutingAssembly());
        });

        Log.Logger = new LoggerConfiguration()
            .ReadFrom.Configuration(builder.Configuration, "Serilog:System")
            .CreateLogger();
        builder.Services.AddSingleton(Log.Logger);
        builder.Host.UseSerilog();
    }

    public void AddServices(WebApplicationBuilder builder)
    {
        builder.Services.AddMvc(opt =>
            {
                opt.Filters.Add<GlobalExceptionFilter>();
                opt.EnableEndpointRouting = false;
            })
            .AddNewtonsoftJson(opt =>
            {
                opt.SerializerSettings.DateFormatString = "yyy-MM-ddTHH:mm:ss.FFFZ";
                opt.SerializerSettings.ReferenceLoopHandling = ReferenceLoopHandling.Ignore;
                opt.SerializerSettings.Converters.Add(new StringEnumConverter());
                opt.SerializerSettings.ContractResolver = new DefaultContractResolver
                {
                    NamingStrategy = new SnakeCaseNamingStrategy()
                };
            });

        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen(opt =>
        {
            opt.SwaggerDoc("v1", new OpenApiInfo
            {
                Title = builder.Configuration.GetSection("Metadata").GetValue<string>("ApiTitle"),
                Version = "v1.0"
            });
        });
    }
}