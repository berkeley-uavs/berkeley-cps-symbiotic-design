"""Detail Routing for UAV tubes and Hubs
The following are the interface for this level of routing problem:
Given: 
    Nodes: location of each node to be connected
    Edges: Netlist of the required connection
Goal:
    Generate hubs and tubes with correct parameters such that all the required connection is connected.

Sample input (QuadCopter)
{
    "Grid":
	"L1": 
	{
		"edges":[[0, 4], [1, 4], [2, 4], [3, 4]]
		"nodes":
		[
		{
			"location":[0,5],
			"type": "P",
		},
		{
			"location":[5,0],
			"type": "P",
		}, 
		{
			"location":[5, 10],
			"type": "P",
		}, 
		{
			"location":[10,5],
			"type": "P",
		},
        {
            "location":[5,5],
			"type": "F",
		}
        ]	
	}

}
"""
from sym_cps.optimizers.routing.tool import Net, Coordinate_3d

class DetailRouter(object):
    def __init__(self, netlist: list[Net], nodes: list[Coordinate_3d]):
        # create grids
        pass





        


