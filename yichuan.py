from random import *
from math import *
import matplotlib.pyplot as plt
import pygame
import time

blocksize = 50
mapsize = 10
obsize = 2
obs = [(7.5,0.5), (3.5,4.5), (4.5,7.5), (7,4), (3,1)]
obstructions = []
children = []
selected = []
generated = []
bestone = (0,0,0)
ans = []
population = 100
generation_max = 100
generation_num = 0
pc = 0.9
pm = 0.3


def mydeepcopy(geti):
    mypath = geti[1]
    mynewpath = []
    for dot in mypath:
        mynewpath.append((dot[0], dot[1]))
    t = (geti[0], mynewpath, geti[2])
    return t


def cross(p1,p2,p3): # 叉积判定
    x1=p2[0]-p1[0]
    y1=p2[1]-p1[1]
    x2=p3[0]-p1[0]
    y2=p3[1]-p1[1]
    return x1*y2-x2*y1


def intersection(x1, x2, y1, y2):
    if (max(x1[0], x2[0]) >= min(y1[0], y2[0])  # 矩形1最右端大于矩形2最左端
            and max(y1[0], y2[0]) >= min(x1[0], x2[0])  # 矩形2最右端大于矩形1最左端
            and max(x1[1], x2[1]) >= min(y1[1], y2[1])  # 矩形1最高端大于矩形2最低端
            and max(y1[1], y2[1]) >= min(x1[1], x2[1])):  # 矩形2最高端大于矩形1最低端
        if (cross(x1, x2, y1) * cross(x1, x2, y2) <= 0
                and cross(y1, y2, x1) * cross(y1, y2, x2) <= 0):
            D = True
        else:
            D = False
    else:
        D = False
    return D


def isvalid(ipath, idotnum):
    for ob in obstructions:
        left = ob[0]
        right = ob[1]
        bottom = ob[2]
        top = ob[3]
        for dot in ipath:
            if left <= dot[0] <= right and bottom <= dot[1] <= top:
                return False
        for i in range(idotnum-1):
            d1 = ipath[i]
            d2 = ipath[i+1]
            if intersection(d1, d2, ob[5], ob[7]) or intersection(d1, d2, ob[4], ob[6]):
                return False
        if intersection((0, 0), ipath[0], ob[5], ob[7]) or intersection((0, 0), ipath[0], ob[4], ob[6]):
            return False
        if intersection((mapsize, mapsize), ipath[idotnum-1], ob[5], ob[7]) or intersection((mapsize, mapsize), ipath[idotnum-1], ob[4], ob[6]):
            return False
    return True


def getadaptation(gpath, gdotnum):
    adapt = 0
    for i in range(gdotnum-1):
        d1 = gpath[i]
        d2 = gpath[i+1]
        adapt += sqrt((d2[0]-d1[0])*(d2[0]-d1[0])+(d2[1]-d1[1])*(d2[1]-d1[1]))
    start = gpath[0]
    end = gpath[-1]
    adapt += sqrt(start[0]*start[0]+start[1]*start[1])
    adapt += sqrt(end[0]*end[0]+end[1]*end[1])
    return 48-adapt


start = time.time()
# initialize the obstructions
for ob in obs:
    obstructions.append([ob[0], ob[0]+2, ob[1], ob[1]+2, (ob[0],ob[1]), (ob[0]+2,ob[1]), (ob[0]+2,ob[1]+2), (ob[0],ob[1]+2)])
# initialize the population
total_adapt = 0
while len(children) != population:
    dotnum = randint(3, 8)
    path = []
    for i in range(dotnum):
        x = uniform(0, mapsize)
        y = uniform(0, mapsize)
        path.append((x, y))
    if isvalid(path, dotnum):
        adaptation = getadaptation(path, dotnum)
        children.append((dotnum, path, adaptation))
        total_adapt += adaptation

while generation_num < generation_max:
    # selection
    #
    print('start selection')
    del selected
    selected = []
    cancha = []
    print("length of children = {}".format(len(children)))
    for i in range(len(children)):
        child = children[i]
        e = population * child[2] / total_adapt
        inte = int(e)
        for i in range(inte):
            selected.append(mydeepcopy(child))
        cancha.append((e - inte, i))

    print("length of cancha = {}".format(len(cancha)))
    cancha.sort(key=lambda x:x[0], reverse=True)

    for i in range(population-len(selected)):
        index = cancha[i][1]
        selected.append(mydeepcopy(children[index]))
    print("length of selected = {}".format(len(selected)))
    # generate
    #
    print("start generation")
    del generated
    generated = []
    for i in range(int(len(selected) / 2)):
        a = selected.pop(randint(0, len(selected)-1))
        b = selected.pop(randint(0, len(selected)-1))
        if random() < pc:
            apath = a[1]
            bpath = b[1]
            acut = randint(1,a[0]-1)
            bcut = randint(1,b[0]-1)
            anewpath = apath[:acut] + bpath[bcut:]
            bnewpath = bpath[:bcut] + apath[acut:]
            anum = len(anewpath)
            bnum = len(bnewpath)
            t = isvalid(anewpath, anum) and isvalid(bnewpath,bnum)
            times = 0
            while t is False:
                times += 1
                if times > 50:
                    break
                acut = randint(1,a[0]-1)
                bcut = randint(1,b[0]-1)
                anewpath = apath[:acut] + bpath[bcut:]
                bnewpath = bpath[:bcut] + apath[acut:]
                anum = len(anewpath)
                bnum = len(bnewpath)
                t = isvalid(anewpath, anum) and isvalid(bnewpath,bnum)
            if times > 50:
                generated.append(a)
                generated.append(b)
                continue
            generated.append((anum, anewpath, 0))
            generated.append((bnum, bnewpath, 0))
        else:
            generated.append(a)
            generated.append(b)
    # variation
    #
    print("start variation")
    for i in range(len(generated)):
        if random() < pm:
            a = generated[i]
            apath = a[1]
            anum = a[0]
            varidot = randint(0, anum-1)
            old = apath[varidot]
            x = uniform(0,mapsize)
            y = uniform(0,mapsize)
            apath[varidot] = (x,y)
            while isvalid(apath, anum) is False:
                apath[varidot] = old
                varidot = randint(0, anum-1)
                old = apath[varidot]
                x = uniform(0,mapsize)
                y = uniform(0,mapsize)
                apath[varidot] = (x,y)
            generated[i] = (anum, apath, 0)
    # calculate the best one
    #
    print("start choose the best one")
    del children
    children = []
    total_adapt = 0
    maxadaptation = 0
    maxindex = -1
    for i in range(len(generated)):
        gene = generated[i]
        adaptation = getadaptation(gene[1], gene[0])
        total_adapt += adaptation
        if maxadaptation < adaptation:
            maxadaptation = adaptation
            maxindex = i
        children.append((gene[0], gene[1], adaptation))
    if maxadaptation > bestone[2]:
        bestone = mydeepcopy(children[maxindex])
    # over
    generation_num += 1
    print("generation num = {}".format(generation_num))
    ans.append(bestone[2])

end = time.time()
print("run time = {}s".format(end-start))
x = range(len(ans))
plt.plot(x,ans)
plt.show()

print(bestone)
pygame.init()
screen = pygame.display.set_mode([blocksize*(mapsize+2),blocksize*(mapsize+2)])
screen.fill([255,255,255])
for i in range(1,14):
    pygame.draw.line(screen, [0,0,0], (blocksize, blocksize*i), (blocksize*(mapsize+1), blocksize*i), 1)
    pygame.draw.line(screen, [0,0,0], (blocksize*i, blocksize), (blocksize*i, blocksize*(mapsize+1)), 1)
for ob in obstructions:
    position = [blocksize*(ob[0]+1), blocksize*(ob[2]+1), blocksize*(ob[1]-ob[0]), blocksize*(ob[3]-ob[2])]
    pygame.draw.rect(screen,[0,0,255], position, 0)
path = bestone[1]
for i in range(len(path)-1):
    d0 = ((path[i][0]+1)*blocksize, (path[i][1]+1)*blocksize)
    d1 = ((path[i+1][0]+1)*blocksize, (path[i+1][1]+1)*blocksize)
    pygame.draw.line(screen, [255,0,0], d0, d1, 1)
start = ((path[0][0]+1)*blocksize, (path[0][1]+1)*blocksize)
end = ((path[-1][0]+1)*blocksize, (path[-1][1]+1)*blocksize)
pygame.draw.line(screen, [255,0,0], (blocksize,blocksize), start, 1)
pygame.draw.line(screen, [255,0,0], end, (blocksize*(mapsize+1),(mapsize+1)*blocksize), 1)
pygame.display.update()
t = input("hello\n")