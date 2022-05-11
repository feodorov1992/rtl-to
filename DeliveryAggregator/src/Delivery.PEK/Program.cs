using Delivery.Common;
using Microsoft.AspNetCore.Mvc.ApplicationParts;
using Microsoft.OpenApi.Models;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseSerilog((_, lc) => lc.WriteTo.Console());

// Add services to the container.
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration, "Serilog:System")
    .CreateLogger();
builder.Services.AddSingleton(Log.Logger);

var commonAssembly = typeof(CommonAssembly).Assembly;
var applicationParts = builder.Services.AddControllers().PartManager.ApplicationParts;
applicationParts.Add(new AssemblyPart(commonAssembly));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(opt =>
{
    opt.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = builder.Configuration.GetSection("Metadata").GetValue<string>("ApiTitle"),
        Version = "v1.0"
    });
});

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();

app.MapControllers();

app.Run();