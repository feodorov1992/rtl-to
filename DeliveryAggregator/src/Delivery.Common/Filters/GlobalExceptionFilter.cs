using System.ComponentModel.DataAnnotations;
using System.Net;
using System.Net.Http.Json;
using System.Net.Mime;
using Delivery.Common.Exceptions;
using Delivery.Common.Responses;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Filters;
using Newtonsoft.Json;
using Serilog;

namespace Delivery.Common.Filters;

public class GlobalExceptionFilter : ExceptionFilterAttribute
{
    public override async Task OnExceptionAsync(ExceptionContext context)
    {
        try
        {
            HttpStatusCode status;
            string error;
                
            var ex = context.Exception;
            
            switch (ex)
            {
                case HttpRequestException hre:
                    error = hre.Message;
                    status = (HttpStatusCode)hre.StatusCode;
                    break;
                
                case NotImplementedException _:
                    status = HttpStatusCode.NotImplemented;
                    error = ExceptionKey.METHOD_NOT_IMPLEMENTED;
                    break;
                
                case System.ComponentModel.DataAnnotations.ValidationException _:
                case Exceptions.ValidationException _:
                    status = HttpStatusCode.BadRequest;
                    error = ExceptionKey.REQUEST_VALIDATION_FAILURE;
                    break;
                
                case CounterpartyClientException cle:
                    status = HttpStatusCode.BadRequest;
                    error = cle.Error;
                    break;
                
                default:
                    status = HttpStatusCode.InternalServerError;
                    error = ex.Message;
                    break;
            }

            Log.Error("ErrorType: " + ex.GetType().Name + "\n"
                      + "ErrorString: " + ex);
            
            
            var response = BasicResponse<object>.Fail(error, ex.Message);
            var json = JsonConvert.SerializeObject(response);
            Log.Error(json);

            var httpResponse = context.HttpContext.Response;
            httpResponse.StatusCode = (int)status;
            httpResponse.ContentType = MediaTypeNames.Application.Json;

            await httpResponse.WriteAsync(json);
            context.ExceptionHandled = true;
        }
        catch (Exception e)
        {
            Log.Error(e, "Error occurred in the global exception filter");
        }
    }
}