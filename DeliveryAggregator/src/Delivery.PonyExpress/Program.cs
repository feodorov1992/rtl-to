using System.Text.Json.Serialization;
using Delivery.Common;
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

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();

app.MapControllers();

app.Run();