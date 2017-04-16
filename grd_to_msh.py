import argparse
import numpy as np

parser = argparse.ArgumentParser('Program to convert the Sentaurus GRD mesh to Gmsh MSH format')
parser.add_argument('input',help='File name of the input GRD file',
                    type=argparse.FileType('r'), nargs='?',
                    default='n15_des_exported.grd')
parser.add_argument('output',help='File name of the output MSH file',
                    type=argparse.FileType('w'), nargs='?',
                    default='n15_des_exported.msh')
args = parser.parse_args()

infile = args.input
outfile = args.output

#----------------------------- READ THE GRD FILE -------------------------------

#Mesh info
dimension = 0
nb_vertices = 0
nb_edges = 0
nb_faces = 0
nb_elements = 0
nb_regions = 0
regions = []

curly_braces_stack = 0

#Discard all lines before the info section
line = infile.readline()
while not 'Info' in line:
    line = infile.readline()

curly_braces_stack += 1

#Read the info section
line = infile.readline()
while not curly_braces_stack == 0:
    if 'dimension' in line:
        line = line.strip()
        columns = line.split('=')
        dimension = int(columns[1].strip())
    elif 'nb_vertices' in line:
        line = line.strip()
        columns = line.split('=')
        nb_vertices = int(columns[1].strip())
    elif 'nb_edges' in line:
        line = line.strip()
        columns = line.split('=')
        nb_edges = int(columns[1].strip())
    elif 'nb_faces' in line:
        line = line.strip()
        columns = line.split('=')
        nb_faces = int(columns[1].strip())
    elif 'nb_elements' in line:
        line = line.strip()
        columns = line.split('=')
        nb_elements = int(columns[1].strip())
    elif 'nb_regions' in line:
        line = line.strip()
        columns = line.split('=')
        nb_regions = int(columns[1].strip())
    elif 'regions' in line and not 'nb_regions' in line:
        line = line.strip()
        columns = line.split(' ')
        i=0
        while not '[' in columns[i]:
            i += 1
        i += 1
        while not ']' in columns[i]:
            regions.append(columns[i].strip('\"'))
            i += 1
    elif '{' in line:
        curly_braces_stack += 1
    elif '}' in line:
        curly_braces_stack -= 1
    line = infile.readline() 

#Mesh data
vertices = np.zeros((nb_vertices, dimension))
edges = [[] for i in range(nb_edges)]
faces = [[] for i in range(nb_faces)]
elements = [[] for i in range(nb_elements)]
element_to_region = [1 for i in range(nb_elements)]

#Discard all lines before the data section
line = infile.readline()
while not 'Data' in line:
    line = infile.readline()

curly_braces_stack += 1

#Read the data section
line = infile.readline()
while not curly_braces_stack == 0:
    
    #Coordinate transformations aren't implemented yet
    if 'CoordSystem' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        while not curly_braces_stack == 1:
            line = infile.readline()
            if '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    #Read the vertices
    if 'Vertices' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        
        #Read nb_vertices number of vertices
        for i in range(nb_vertices):
            line = infile.readline()
            line = line.strip()
            columns = line.split()
            for j in range(dimension):
                vertices[i][j] = float(columns[j].strip())

        #Reach end of Vertices section
        while not curly_braces_stack == 1:
            line = infile.readline()
            if '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    #Read the edges
    if 'Edges' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        
        #Read nb_edges number of edges
        for i in range(nb_edges):
            line = infile.readline()
            line = line.strip()
            columns = line.split()
            for j in range(2):
                edges[i].append(int(columns[j].strip()))

        #Reach end of Edges section
        while not curly_braces_stack == 1:
            line = infile.readline()
            if '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    #Read the faces
    if 'Faces' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        
        #Read nb_faces number of faces
        for i in range(nb_faces):
            line = infile.readline()
            line = line.strip()
            columns = line.split()
            for j in range(len(columns)):
                faces[i].append(int(columns[j].strip()))

        #Reach end of Faces section
        while not curly_braces_stack == 1:
            line = infile.readline()
            if '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    #Read the elements
    if 'Elements' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        
        #Read nb_elements number of elements
        for i in range(nb_elements):
            line = infile.readline()
            line = line.strip()
            columns = line.split()
            for j in range(len(columns)):
                elements[i].append(int(columns[j].strip()))

        #Reach end of Elements section
        while not curly_braces_stack == 1:
            line = infile.readline()
            if '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    #Read the regions
    if 'Region' in line and curly_braces_stack == 1:
        curly_braces_stack += 1
        region_name = line.split('\"')[1]
        region_number = 1
        for i in range(len(regions)):
            if region_name == regions[i]:
                region_number = i+1
                break
        
        while not curly_braces_stack == 1:
            line = infile.readline()
            if 'Elements' in line and curly_braces_stack == 2:
                curly_braces_stack += 1
                while not curly_braces_stack == 2:
                    line = infile.readline()
                    if '{' in line:
                        curly_braces_stack += 1
                    elif '}' in line:
                        curly_braces_stack -= 1
                    else:
                        line = line.strip()
                        columns = line.split()
                        for j in range(len(columns)):
                            element_to_region[int(columns[j])] = region_number
                
            elif '{' in line:
                curly_braces_stack += 1
            elif '}' in line:
                curly_braces_stack -= 1
        line = infile.readline()

    elif '{' in line:
        curly_braces_stack += 1
    elif '}' in line:
        curly_braces_stack -= 1
    line = infile.readline() 

infile.close()

#--------------------------- DONE READING GRD FILE ----------------------------

#---------------------------- WRITE THE MSH FILE ------------------------------

tdr_to_msh_elem_type = {2:2, 5:4, 1:1}

line = '$MeshFormat\n'
outfile.write(line)
line = '2.2 0 8\n'
outfile.write(line)
line = '$EndMeshFormat\n'
outfile.write(line)

line = '$Nodes\n'
outfile.write(line)
line = '%d\n' % nb_vertices
outfile.write(line)
for i in range(nb_vertices):
    if dimension == 3:
        line = '%d %.16g %.16g %.16g\n' % (i+1, vertices[i][0], vertices[i][1], vertices[i][2])
    elif  dimension == 2:
        line = '%d %.16g %.16g 0\n' % (i+1, vertices[i][0], vertices[i][1])
    elif  dimension == 1:
        line = '%d %.16g 0 0\n' % (i+1, vertices[i][0])
    outfile.write(line)
line = '$EndNodes\n'
outfile.write(line)

line = '$Elements\n'
outfile.write(line)
line = '%d\n' % nb_elements
outfile.write(line)
for i in range(nb_elements):
    points_el = []
    faces_el = []
    edges_el = []
    line = '%d %d 2 2 %d' % (i+1, tdr_to_msh_elem_type[elements[i][0]], element_to_region[i])

    if elements[i][0] == 5:
        dimension = 3
    elif elements[i][0] == 2:
        dimension = 2
    elif elements[i][0] == 1:
        dimension = 1

    if dimension == 3:
        for j in range(len(elements[i])-1):
            temp = elements[i][j+1]
            if temp < 0:
                temp = abs(temp+1)
            faces_el.append(temp)
        for j in range(len(faces_el)):
            for k in range(len(faces[faces_el[j]])-1):
                temp = faces[faces_el[j]][k+1]
                if temp < 0:
                    temp = abs(temp+1)
                if temp not in edges_el:
                    edges_el.append(temp)
        for j in range(len(edges_el)):
            for k in range(len(edges[edges_el[j]])):
                temp = edges[edges_el[j]][k]
                if temp not in points_el:
                    points_el.append(temp)
    elif dimension == 2:
        for j in range(len(elements[i])-1):
            temp = elements[i][j+1]
            if temp < 0:
                temp = abs(temp+1)
            edges_el.append(temp)
        for j in range(len(edges_el)):
            for k in range(len(edges[edges_el[j]])):
                temp = edges[edges_el[j]][k]
                if temp not in points_el:
                    points_el.append(temp)
    elif dimension == 1:
        for j in range(len(elements[i])-1):
            points_el.append(abs(elements[i][j+1]))

    for j in range(len(points_el)):
        line += ' %d' % (points_el[j]+1)
    line += '\n'
    
    outfile.write(line)
line = '$EndElements\n'
outfile.write(line)

outfile.close()
