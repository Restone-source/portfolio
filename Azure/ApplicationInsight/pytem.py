import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_INSTANCE_ID, Resource
import pandas as pd

import requests

# url = "https://prices.azure.com/api/retail/prices?currencyCode='KRW'&$filter=serviceName eq 'Virtual Machines' and armSkuName eq 'Standard_A3' and armRegionName eq 'koreacentral' and Currencycode eq 'KRW'"
# r = requests.get(url)
# d = r.json()
# resource = pd.DataFrame.from_dict(d['Items'])
# row_result = resource[resource['type']=='Consumption']
# col_result = row_result[['unitPrice','armSkuName','skuName']]
# print(col_result)

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: "my-helloworld-service",
                SERVICE_NAMESPACE: "my-namespace",
                SERVICE_INSTANCE_ID: "my-instance",
            }
        )
    )
)

exporter = AzureMonitorTraceExporter.from_connection_string(
    "InstrumentationKey=1ad571f4-c1e0-4888-80d0-82c8a722be18;IngestionEndpoint=https://koreacentral-0.in.applicationinsights.azure.com/;LiveEndpoint=https://koreacentral.livediagnostics.monitor.azure.com/"
)

#trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# with tracer.start_as_current_span("anotherspan"):
#     r = requests.get(url)
#     print(col_result)

with tracer.start_as_current_span("foo"):
    with tracer.start_as_current_span("bar"):
        with tracer.start_as_current_span("baz"):
            print("Hello world from OpenTelemetry Python!")