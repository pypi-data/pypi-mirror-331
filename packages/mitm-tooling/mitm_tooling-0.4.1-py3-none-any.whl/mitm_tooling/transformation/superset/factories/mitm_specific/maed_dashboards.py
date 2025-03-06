from mitm_tooling.representation import Header
from mitm_tooling.transformation.superset.definition_bundles import SupersetDatasourceBundle
from mitm_tooling.transformation.superset.definitions import SupersetDashboardDef, SupersetChartDef
from mitm_tooling.transformation.superset.factories.dashboard import mk_dashboard_def, mk_dashboard_chart
from mitm_tooling.transformation.superset.factories.mitm_specific.maed_charts import mk_maed_charts


def mk_maed_dashboard(header: Header, datasource_bundle: SupersetDatasourceBundle) -> tuple[SupersetDashboardDef, list[SupersetChartDef]]:
    charts = mk_maed_charts(header, datasource_bundle)
    chart_grid = [[mk_dashboard_chart(chart_uuid=charts['objects-pie'].uuid, width=4, height=50),
                   mk_dashboard_chart(chart_uuid=charts['event-count-ts'].uuid, width=4, height=50),
                   mk_dashboard_chart(chart_uuid=charts['measurement-count-ts'].uuid, width=4, height=50)],
                  [mk_dashboard_chart(chart_uuid=charts['ts'].uuid, width=12, height=100)]]
    return mk_dashboard_def('MAED Dashboard', chart_grid=chart_grid, native_filters=[],
                            description='A rudimentary dashboard to view MAED data.'), list(charts.values())
