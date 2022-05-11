FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-backend
WORKDIR /build
COPY . ./

WORKDIR /build/Delivery.SDEK
RUN dotnet publish -c Release -o /app

FROM base AS final
WORKDIR /app
COPY --from=build-backend /app .
ENTRYPOINT ["dotnet", "Delivery.SDEK.dll"]