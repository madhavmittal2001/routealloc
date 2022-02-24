# %%
import requests
from pprint import pprint

class Location:
  def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class Stop:
  def __init__(self, loc, drop, id):
        self.loc = loc
        self.drop = drop
        self.id = id

class Vehicle:
  def __init__(self, id, status, loc, route, max_capacity, current_capacity, volume, current_volume, consignments):
    self.id = id
    self.status = status
    self.loc = loc
    self.route = route
    self.max_capacity = max_capacity
    self.current_capacity = current_capacity
    self.volume = volume
    self.current_volume = current_volume
    self.consignments = consignments

class Consignment:
  def __init__(self, id, status, pickup_location, drop_location, pickup_date, drop_date, pickup_time, drop_time, weight, volume):
    self.id = id
    self.status = status
    self.pickup_location= pickup_location
    self.drop_location = drop_location
    self.pickup_date = pickup_date
    self.drop_date = drop_date
    self.pickup_time = pickup_time
    self.drop_time = drop_time
    self.weight = weight
    self.volume = volume

class Route:
  def __init__(self, start_point, end_point, sequence_of_points):
    self.start_point = start_point
    self.end_point = end_point
    self.sequence_of_points = sequence_of_points

# %%
def distance_matrix(coords):
    #calculates distance matrix for the given array of coords
    url = 'http://router.project-osrm.org/table/v1/driving/'
    for c in range(len(coords)) :
        lng = str(coords[c].lon)
        lat = str(coords[c].lat)
        if c == 0 :
            url = url+lng+','+lat
        else :
            url = url +';'+lng + ',' + lat
    
    url = url+'?annotations=distance'
     
    global distMat
    distMat = requests.get(url).json()['distances'];
    return distMat

# %%
def get_point_point_dist(a, b):
    global coords
    global distMat
    # get from distance matrix generated using osrm
    i=0
    j=0
    for c in range(len(coords)) :
        lng = coords[c].lon #longitude
        lat = coords[c].lat #latitude
        if(a.lon == lng and a.lat ==lat) :
            i=c
        if(b.lon == lng and b.lat == lat):
            j=c
    return distMat[i][j]

# %%
def can_be_allocated(consignment, v):
    global vehicle_list
    if consignment.weight > vehicle_list[v].current_capacity:
        return False
    if consignment.volume > vehicle_list[v].current_volume:
        return False
    return True

# %%
# def get_polyline_point_dist(route, point):
    
#     return True

# %%
def allocate_consignments_to_empty_vehicles(vehicles_list, consignment_list):
    local_consignment_list = consignment_list[:]
    veh_set = list(range(len(vehicles_list)))
    for c in consignment_list:
        c_vehicles = veh_set[:]
        n_veh = c_vehicles[0]
        min_distance = get_point_point_dist(c.pickup_location, vehicles_list[n_veh].loc)
        for veh in c_vehicles:
            distance = get_point_point_dist(c.pickup_location, vehicles_list[veh].loc)
            if distance < min_distance:
                n_veh = veh
                min_distance = distance
        c_vehicles.remove(n_veh)
        c_allocated = False
        while not c_allocated:
            if can_be_allocated(c, n_veh):
                c_allocated = True
                local_consignment_list.remove(c)
                vehicle_list[n_veh].consignments.append(c.id)
                vehicle_list[n_veh].current_capacity -= c.weight
                vehicle_list[n_veh].current_volume -= c.volume
            else:
                n_veh = c_vehicles[0]
                min_distance = get_point_point_dist(c.pickup_location, vehicles_list[n_veh].loc)
                for veh in c_vehicles:
                    distance = get_point_point_dist(c.pickup_location, vehicles_list[veh].loc)
                    if distance < min_distance:
                        n_veh = veh
                        min_distance = distance
                c_vehicles.remove(n_veh)
            if not c_vehicles:
                break
    return local_consignment_list, vehicles_list

# %%
# def constraints_check(routewith_i,j):
#   if(j.drop):
#     return 1
#   for k in routewith_i.sequence_of_points:
#     if(k.drop and k.id==j):
#         return 0
#   return 1

# %%
def CVRPhelper(stops, V):
    
    savingslist = []
    
    for i in range(len(stops)):
        for j in range(len(stops)):
            savingslist.append([get_point_point_dist(stops[i], V.loc) + get_point_point_dist(V.loc, stops[j]) - get_point_point_dist(stops[i], stops[j]), (i, j)])
    savingslist.sort(reverse = True, key = lambda x: x[0])
    
    all_routes = []
    for i in range(len(stops)):
        all_routes.append(Route(i, i, [i]))
    
    # i = 0
    # while i < len(stops):
    #     all_routes.append(Route(i, i+1, [i, i+1]))
    #     i += 2
    
    for l in savingslist:
        
        # for ro in all_routes:
        #     pprint(vars(ro))
        
        i = l[1][0]
        j = l[1][1]
        
        j_route=0
        i_route=0
        
        # routewith_i=Route()
        # routewith_j=Route()
        # route_ij=Route(0, 0, [])
        
        for k in all_routes:
            if(i in k.sequence_of_points):
                i_route=1
                routewith_i=k
                break
        for k in all_routes:
            if(j in k.sequence_of_points):
                j_route=1
                routewith_j=k
                break
        
        #case1 no routes assigned for both
        if(not (i_route or j_route)):
            all_routes.append(Route(i, j, [i,j]))
            continue
        
        #3
        if(i_route and j_route):
            if routewith_i == routewith_j :
                continue
            if(routewith_i.end_point==i and routewith_j.start_point==j):
                all_routes.append(Route(routewith_i.start_point, routewith_j.end_point, routewith_i.sequence_of_points + routewith_j.sequence_of_points))
                # routewith_i.end_point=routewith_j.end_point
                # routewith_i.sequence_of_points.extend(routewith_j.sequence_of_points)
                # route_ij=copy.copy(routewith_i)
                all_routes.remove(routewith_j)
                all_routes.remove(routewith_i)
                # all_routes.append(route_ij)
            continue
                
        #case 2
        if(i_route):
            if(routewith_i.end_point==i):        
                routewith_i.end_point=j
                routewith_i.sequence_of_points.append(j)
                # route_ij=copy.copy(routewith_i)
                # all_routes.append(route_ij)   
            continue
        
        if(j_route):
            if(routewith_j.start_point==j):
                routewith_j.start_point=i
                routewith_j.sequence_of_points.insert(0,i) 
                # route_ij=copy.copy(routewith_j)
                # all_routes.append(route_ij)    
    
    
    return all_routes

# %%
def CVRP(V): # V - vehicle
    global consignment_list
    savingslist = []
    pstops = []
    dstops = []
    cons = V.consignments        
            
    for consignment_id in cons:
        for c in consignment_list:
            if c.id == consignment_id:
                pstops.append(c.pickup_location)
                dstops.append(c.drop_location)
                break

    proute = CVRPhelper(pstops, V)
    # print("****************")
    droute = CVRPhelper(dstops, V)
    
                
    for route in proute:
        # pprint(vars(route))
    
        for stop in route.sequence_of_points:
            V.route.append((pstops[stop], cons[stop], 'P'))
    for route in droute:
        for stop in route.sequence_of_points:
            V.route.append((dstops[stop], cons[stop], 'D'))

    return V

# %%
def get_shortest(distance_list):
    shortest = min(distance_list, key = lambda x: x[0])
    return shortest[1]

# %%
# def allocate_consignment(vehicles_list, consignment_id):
#     return True

# %%
def route_alloc(vehicles_list, consignment_list):
    all_empty = True
    moving_vehicles = []
    unassigned_consignments_list = consignment_list
    for vehicle in vehicles_list:
        if vehicle.consignments:
            all_empty = False
        if vehicle.status == True:
            moving_vehicles.append(vehicle)
    if all_empty and not moving_vehicles:
        unassigned_consignments_list, vehicles_list = allocate_consignments_to_empty_vehicles(vehicles_list, consignment_list)
    return unassigned_consignments_list, vehicles_list
    # while unassigned_consignments_list:
    #     c = unassigned_consignments_list[0]
    #     if len(moving_vehicles) != len(vehicles_list):
    #         distance_list = []
    #         for vehicle in vehicles_list:
    #             if vehicle.route:
    #                 distance_list.append(get_polyline_point_dist(vehicle.route, c.pickup_location), vehicle)
    #             else:
    #                 distance_list.append(get_polyline_point_dist(vehicle.loc, c.pickup_location), vehicle)
    #         vehicle_to_be_assigned = get_shortest(distance_list)
    #         if vehicle_to_be_assigned.status == True:
    #             allocate_consignment(moving_vehicles, c.id)
    #             #   vehicle_list
    #     else:
    #         allocate_consignment(vehicles_list, c.id)
            #   vehicle_list

# %%
vehicle_list = []
consignment_list = []

inptfile = open("inpt1.txt", 'r')
inpt = inptfile.readlines()

vn = int(inpt[0])
cn = int(inpt[1])
base = 2
for i in range(vn):
    temp = inpt[base + i].split()
    id = int(temp[0])
    status = not (temp[1].strip() == "Idle")
    lat = float(temp[2])
    lon = float(temp[3])
    route = []
    consignments = []
    capacity = float(temp[4])*1000
    volume = float(temp[5])
    curr_capacity = float(temp[6])*1000
    vehicle_list.append(Vehicle(id, status, Location(lat, lon), route, capacity, curr_capacity, volume, volume, consignments))

base = base + vn
for i in range(cn):
    temp = inpt[base + i].split()
    id = int(temp[0])
    status = (temp[1].strip() == "Allocated")
    plat = float(temp[2])
    plon = float(temp[3])
    dlat = float(temp[4])
    dlon = float(temp[5])
    weight = float(temp[6])
    consignment_list.append(Consignment(id, status, Location(plat, plon), Location(dlat, dlon), 0, 0, 0, 0, weight, 0))

# %%
coords = [x.loc for x in vehicle_list]
coords.extend([x.pickup_location for x in consignment_list])
coords.extend([x.drop_location for x in consignment_list])

import folium

map = folium.Map()

for c in coords:
    folium.Marker(location = (c.lat, c.lon)).add_to(map)

map.fit_bounds(map.get_bounds())

distMat = distance_matrix(coords)

# %%
# map

# %%
unallocated_cons, vehicle_list = route_alloc(vehicle_list, consignment_list)

# %%
#### Print all vehicles after allocation of consignments (ROUTE NOT ALLOCATED) ####
# for v in vehicle_list:
#     pprint(vars(v))

# %%
for v in vehicle_list:
    print("Vehicle", v.id)
    if not v.consignments :
        print(0)
    else :
        print(len(v.consignments), *v.consignments)
        v1 = CVRP(v)
        for stop in v1.route:
            print(stop[1], stop[2], stop[0].lat, stop[0].lon)


