#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import csv
import math
import sys
from abc import abstractmethod
import os
import pathlib
import time

#INSTALLED PACKAGE IMPORTS
import carla
from shapely.geometry import Polygon
from shapely.affinity import rotate
import numpy as np
import pandas as pd

#IMPORTS FROM THIS PACKAGE
from ce_python.simple_agent import SimpleAgent

# ==============================================================================
# -- Grid ---------------------------------------------------------------
# ==============================================================================

class Grid(object):
    def __init__(self, top: float, bottom: float, left: float, right: float, grid_height = 1, draw_time: int = 0):
        #this will be a 20x20 grid
        """
        top/bottom are x values
        left/right are y values
        assume axes look like
        x
        ^
        |
        |
        |
        --------> Y
        """
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.box_width = abs(self.right - self.left)/20
        self.box_height = abs(self.top - self.bottom)/20 

        self.grid_height = grid_height

    def return_location_from_grid(self, i: int, j: int):
        center_point_y = self.left + self.box_width*(j) + self.box_width/2
        center_point_x = self.top - self.box_height*(i) - self.box_height/2
        location = carla.Location(x=center_point_x,y=center_point_y,z=self.grid_height)
        return location
    
    def return_grid_from_location(self, location):
        i = 0
        j = 0
        for index in range(0,19):
            if(location.x < self.top - self.box_height * (index)): i=index
            if(location.y > self.left + self.box_width* (index)): j=index
        return (i,j)
    
    @staticmethod
    def return_coords_from_point(point):
        i = math.floor(int(point)/20)
        j = int(point) % 20
        return (i,j)

    @staticmethod
    def return_point_from_coords(i, j):
        return i * 20 + j


# ==============================================================================
# -- World ---------------------------------------------------------------
# ==============================================================================

class World(object):

    def __init__(self, carla_world, grid):
        self.world = carla_world
        self._grid = grid

        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        
        self.ego = None
        self.adversary = None
    
    def destroy(self):
        actors = [
            self.adversary,
            self.ego]
        for actor in actors:
            if actor is not None:
                actor.destroy()

    def draw_location_on_grid(self, location, str_to_draw, draw_time = 10):
        #self.world.debug.draw_point(location,size=0.2,color=carla.Color(0,255,0),life_time=draw_time)
        self.world.debug.draw_string(location,str_to_draw,draw_shadow=False,color=carla.Color(0,255,0),life_time=draw_time)


    def draw_grid(self, draw_time = 10):
        #draw vertical lines
        y=self._grid.left
        for i in range(0,21):
            self.world.debug.draw_line(carla.Location(x=self._grid.top,y=y,z=self._grid.grid_height), carla.Location(x=self._grid.bottom,y=y,z=self._grid.grid_height), thickness=0.1, color=carla.Color(255,0,0), life_time=draw_time)
            y+=self._grid.box_width
        #draw horizontal lines
        x=self._grid.bottom
        for i in range(0,21):
            self.world.debug.draw_line(carla.Location(x=x,y=self._grid.left,z=self._grid.grid_height), carla.Location(x=x,y=self._grid.right,z=self._grid.grid_height), thickness=0.1, color=carla.Color(255,0,0), life_time=draw_time)
            x+=self._grid.box_height
    
    def draw_points_and_locations(self, points):
        counter = 0
        for point in points:
            self.world.debug.draw_point(point.location,size=0.2,color=carla.Color(255,255,255),life_time=30)
            #self.world.debug.draw_string(point.location + carla.Location(z=3),str(point.location.x)+',\n'+str(point.location.y),color=carla.Color(255,0,0),life_time=30)
            self.world.debug.draw_string(point.location + carla.Location(z=3),str(counter),color=carla.Color(255,0,0),life_time=30)
            counter += 1
    
    def draw_spawn_point_locations(self):
        spawn_points = self.map.get_spawn_points()
        for i in range(len(spawn_points)):
            self.world.debug.draw_string(spawn_points[i].location,f"{i}",life_time = 30)

# ==============================================================================
# -- Scenario ---------------------------------------------------------------
# ==============================================================================

class Scenario:
    SPEED_FACTOR = 3
    DEBUG = False

    def __init__(self, file):
        self.file = file
        self.point_array = []
        self.speed_array = []
        self.destination_array = []

        self.feature_vector = []
        self.dataframe = None

        self.host = 'localhost'
        self.port = 2004
        self.world = None
        
        self.read_file()
    
    def read_file(self):
        with open(self.file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                self.point_array.append(row[1])
                self.speed_array.append(float(row[2]) * 3.6 * Scenario.SPEED_FACTOR)
    
    def convert_points_to_locations(self):
        for point in self.point_array:
            i, j = Grid.return_coords_from_point(point) 
            dest = self.world._grid.return_location_from_grid(i,j)
            self.destination_array.append(dest)

    def game_loop(self):
        try:
            client = carla.Client(self.host, self.port)
            client.set_timeout(10.0)

            sim_world = client.get_world()

            settings = sim_world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)

            #grid = Grid(30,-100,24,40,11,draw_time=10)
            grid = Grid(25,-95,5,49,11)
            self.world = World(sim_world, grid)
            self.convert_points_to_locations()
            if(Scenario.DEBUG): self.world.draw_grid(draw_time=30)

            # Spawn the actors
            blueprints = self.world.world.get_blueprint_library()

            adversary_blueprint=blueprints.filter("vehicle.jeep.wrangler_rubicon")[0]
            adversary_blueprint.set_attribute('role_name', 'adversary')

            ego_blueprint = blueprints.filter("vehicle.dodge.charger_police")[0]
            ego_blueprint.set_attribute('role_name','ego')

            ego_spawn_point = carla.Transform(self.world._grid.return_location_from_grid(0,12),carla.Rotation())
            ego_spawn_point.location.z += 2
            ego_spawn_point.rotation.yaw += 180
            self.world.ego = self.world.world.try_spawn_actor(ego_blueprint, ego_spawn_point)

            adversary_spawn_point = carla.Transform(self.destination_array[0],carla.Rotation())
            adversary_spawn_point.location.z += 2
            adversary_spawn_point.rotation.yaw += 180
            self.world.adversary = self.world.world.try_spawn_actor(adversary_blueprint,adversary_spawn_point)

            #This is necessary to ensure vehicle "stabilizes" after "falling"
            for i in range (0,30):
                self.world.world.tick()
            if(Scenario.DEBUG):
                for i in range(len(self.destination_array)):
                    if(i==0):
                        self.world.draw_location_on_grid(self.destination_array[i],'START',draw_time=7)
                    elif(i==len(self.destination_array)-1):
                        self.world.draw_location_on_grid(self.destination_array[i],'END',draw_time=7)
                    else: self.world.draw_location_on_grid(self.destination_array[i],str(i),draw_time=7)
            
            self.execute_scenario()
        
        finally:
            self.write_features()
            if self.world is not None:
                settings = self.world.world.get_settings()
                settings.synchronous_mode = False
                settings.fixed_delta_seconds = None
                self.world.world.apply_settings(settings)

                self.world.destroy()
        
    def execute_scenario(self):
        #set up ego
        ego_destination_array = []
        for i in range(19):
            ego_destination_array.append(self.world._grid.return_location_from_grid(i,12))
        ego_speed_array = [1.0,2.0,3.0]*10
        ego_speed_array = [i * 3.6 * Scenario.SPEED_FACTOR for i in ego_speed_array]
        
        if(Scenario.DEBUG):
            for pt in ego_destination_array:
                self.world.world.debug.draw_string(pt,'X',draw_shadow=False,color=carla.Color(0,0,255),life_time=7)
        
        dest_index = 1
        ego_dest_index = 1

        adversary_agent = SimpleAgent(self.world.adversary, self.destination_array[dest_index], target_speed=self.speed_array[dest_index])

        ego_agent = SimpleAgent(self.world.ego, ego_destination_array[ego_dest_index], target_speed=ego_speed_array[ego_dest_index-1])

        ego_done = False
        while True:
            self.world.world.tick()
            self.get_features()
            
            if adversary_agent.done():
                
                if (dest_index >= len(self.destination_array)-1):
                        #print("Adversary's route is complete, breaking out of loop")
                        break
                else:
                    dest_index += 1
                    new_dest = self.destination_array[dest_index]
                    target_speed = self.speed_array[dest_index] 
                    
                    adversary_agent.set_destination(new_dest)
                    adversary_agent.set_target_speed(target_speed)
            
            if ego_agent.done():
                if (ego_dest_index >= len(ego_destination_array)-1):
                    ego_done = True
                else:
                    ego_dest_index += 1
                    ego_agent.set_destination(ego_destination_array[ego_dest_index])
                    ego_agent.set_target_speed(ego_speed_array[ego_dest_index-1])


            control = adversary_agent.run_step()
            control.manual_gear_shift = False
            self.world.adversary.apply_control(control)

            if(not ego_done):
                self.world.ego.apply_control(ego_agent.run_step())
    
    def get_features(self):
        frame_feature_vec = []
        snapshot = self.world.world.get_snapshot()
        ego_snapshot = snapshot.find(self.world.ego.id)
        adv_snapshot = snapshot.find(self.world.adversary.id)
        frame_feature_vec.append(snapshot.frame)

        (accident,distance,angle) = self.bounding_box_calcs([ego_snapshot, adv_snapshot])
        frame_feature_vec.append(accident)
        frame_feature_vec.append(distance)
        frame_feature_vec.append(angle)

        actors = []
        actors.append(ego_snapshot)
        actors.append(adv_snapshot)

        for a in actors:
            vel = a.get_velocity() #m/s
            accel = a.get_acceleration() #m/s^2
            ang_vel = a.get_angular_velocity() #deg/s
            frame_feature_vec.append(vel.x)
            frame_feature_vec.append(vel.y)
            frame_feature_vec.append(vel.z)
            frame_feature_vec.append(accel.x)
            frame_feature_vec.append(accel.y)
            frame_feature_vec.append(accel.z)
            frame_feature_vec.append(ang_vel.x)
            frame_feature_vec.append(ang_vel.y)
            frame_feature_vec.append(ang_vel.z)
        self.feature_vector.append(frame_feature_vec)
        return frame_feature_vec
    
    def bounding_box_calcs(self, actor_snapshots):
        bounding_boxes = []
        for actor_snapshot in actor_snapshots:
            actual_actor = self.world.world.get_actor(actor_snapshot.id)
            bb = [actual_actor.bounding_box.extent.x,actual_actor.bounding_box.extent.y,actual_actor.bounding_box.extent.z]
            bounding_boxes.append((carla.BoundingBox(actor_snapshot.get_transform().location,carla.Vector3D(y=bb[0],x=bb[1],z=bb[2])),actor_snapshot.get_transform(),actual_actor.attributes.get('role_name')))

        polygons = {}
        transforms = {}
        for bb in bounding_boxes:
            vertices = bb[0].get_local_vertices()
            coords = []
            for vert in vertices:
                if(vert.z > 0):
                    coords.append((vert.x,vert.y))
            coords_copy = coords[:]
            coords[-2] = coords_copy[-1]
            coords[-1] = coords_copy[-2]
            p = Polygon(coords)
            carla_yaw = bb[1].rotation.yaw
            if(carla_yaw > 0):
                p = rotate(p,carla_yaw - 90)
            elif(carla_yaw < 0):
                p = rotate(p,abs(carla_yaw) + 90)
            polygons[bb[2]] = p
            transforms[bb[2]] = bb[1]
        
        ego_vec = (transforms['ego'].get_forward_vector().x,transforms['ego'].get_forward_vector().y)
        diff_vec = transforms['adversary'].location - transforms['ego'].location 
        angle = Scenario.angle_between(ego_vec,(diff_vec.x,diff_vec.y))
        dist = polygons['ego'].distance(polygons['adversary'])
        accident = polygons['ego'].intersects(polygons['adversary'])
        return (accident, dist, angle)
    
    @abstractmethod
    #pass the ego vector first
    def angle_between(v1,v2):
        v1_u = v1/np.linalg.norm(v1)
        v2_u = v2/np.linalg.norm(v2)
        angle =  math.degrees(math.atan2(v1_u[0],v1_u[1]) - math.atan2(v2_u[0],v2_u[1]))
        if(angle < 0 and abs(angle) > 180): angle +=360
        if(angle > 180): angle = angle-360
        return angle
    
    def write_features(self):
        headers = ['frame', 'intersect','distance','angle', 
                   'ego_vel_x','ego_vel_y','ego_vel_z','ego_accel_x','ego_accel_y','ego_accel_z','ego_ang_vel_x','ego_ang_vel_y','ego_ang_vel_z',
                   'adv_vel_x','adv_vel_y','adv_vel_z','adv_accel_x','adv_accel_y','adv_accel_z','adv_ang_vel_x','adv_ang_vel_y','adv_ang_vel_z']
        self.dataframe = pd.DataFrame(data = self.feature_vector, columns=headers)
        df = self.dataframe
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(),"features\\")
        
        label=None
        if("perturbed" in self.file):
            label = "1"
        elif("vanilla" in self.file):
            label = "0"
        else:
            raise Exception("File name doesn't have 'vanilla' or 'perturbed' in it!")
        name_string = os.path.split(self.file)[1].split('.')[0]
        file_name = f"{name_string}_{label}.csv"
        full_path = os.path.join(self.data_path,file_name)
        self.file_name = full_path
        df.to_csv(full_path)