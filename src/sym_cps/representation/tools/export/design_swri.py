import json

from sym_cps.shared.paths import output_folder

# def generate_design_swri_file(design: DConcrete) -> dict[str, str]:
#     """ Generate design_swri_orog.json format file from a concrete design
#         design: the concrete design exporting to design_swri_orog.json file
#         output_path: file path for the export file.
#     """
#     design_swri_data = {}

#     """ Storing the design name"""
#     design_swri_data["name"] = design.name

#     """Storing parameters"""
#     data_parameters: list = []

#     for component in design.components:
#         for parameter_id, parameter in component.parameters.items():
#             data_parameters.append(
#                 {
#                     "parameters_name": f"{component.id}_{parameter.c_parameter.name}",
#                     "value":  str(parameter.value),
#                     "component_properties": {
#                         "component_name": component.id,
#                         "component_property": parameter.c_parameter.name
#                     }
#                 }
#             )
#     design_swri_data["parameters"] = data_parameters

#     """Storing components"""
#     data_components: list[dict[str, str]] = []
#     for component in design.components:
#         data_components.append(
#             {
#                 "component_instance": component.id,
#                 "component_type": component.c_type.id,
#                 "component_choice": component.model
#             }
#         )
#     design_swri_data["components"] = data_components

#     """Storing connections"""
#     data_connections: list[dict[str, str]] = []
#     for connection in design.connections:
#         data_connections.append(
#             {
#                 "from_ci": connection.component_a.id,
#                 "from_conn": connection.connector_a.name,
#                 "to_ci": connection.component_b.id,
#                 "to_conn": connection.connector_b.name
#             }
#         )
#     design_swri_data["connections"] = data_connections
#     return design_swri_data


if __name__ == "__main__":
    from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs

    c_library, designs = parse_library_and_seed_designs()

    for design_name, (design_concrete, design_topology) in designs.items():
        output_name = design_name + "_design_swri.json"
        output_path = output_folder / "seed_designs" / output_name
        design_swri_data = design_concrete.to_design_swri
        # print(design_concrete)
        with open(output_path, "w") as output_file:
            json.dump(design_swri_data, output_file, indent=4)
