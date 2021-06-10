import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# fig, ax = plt.subplots(figsize = (10,5))
# ax.bar(wins_count.keys(), wins_count.values(), width=0.4)
#Now the trick is here.
#plt.text() , you need to give (x,y) location , where you want to put the numbers,
#So here index will give you x pos and data+1 will provide a little gap in y axis.

# plt.savefig("small-normal")

def split_data(data):
    data = data.split(", ")
    
    wins_count = {}

    for i in range(0, len(data), 25):
        batch = data[i: i+25]
        wins = filter(lambda score: score == "Win", batch)
        wins_count[len(wins_count) + 1] = len(wins)

    return wins_count

def plot_wins(small, medium, color):
    small_wins = {i+1: small[i] for i in range(len(small)) }
    medium_wins = {i+1: medium[i] for i in range(len(medium)) }

    plt.plot(small_wins.keys(), small_wins.values(), color+"-")
    plt.plot(small_wins.keys(), small_wins.values(), color+".", markersize=15)

    plt.plot(medium_wins.keys(), medium_wins.values(), color+"--")
    plt.plot(medium_wins.keys(), medium_wins.values(), color+".", markersize=15)

    axes = plt.gca()
    axes.set_ylim([0,25])
    axes.set_xlim([0.5, 5.5])
    plt.legend()
    print("SMALL: ", small_wins.values())
    print("\nMEDIUM: ", medium_wins.values())
    # for index, data in enumerate(wins_count.values()):
    #     plt.text(x=index+0.9 , y=data+1 , s=str(data) , fontdict=dict(fontsize=5))
    # plt.tight_layout()
    # plt.title("\nSMALL GRID: $\gamma$ variations")


plt.figure()

wins = [
[14, 13, 16, 18, 13],
[14, 11, 11, 7, 13],
[20, 17, 18, 19, 20],
[12, 14, 15, 14, 15],
[18, 21, 16, 16, 13],
[7, 6, 7, 3, 4]
]




#0.0
plot_wins([14, 13, 16, 18, 13],
[14, 11, 11, 7, 13],
    "b")

#0.04
plot_wins(
[20, 17, 18, 19, 20],
[12, 14, 15, 14, 15],
    "g")

#0.1
plot_wins(
[18, 21, 16, 16, 13],
[7, 6, 7, 3, 4], "r")

variable = "R(a)"

blue = mpatches.Patch(color='b', label=variable+' = 0.00')
black = mpatches.Patch(color='g', label=variable+' = -0.04')
red = mpatches.Patch(color='r', label=variable+' = -0.10')
plt.legend(handles=[blue, black, red])

plt.xlabel("Run count")
plt.ylabel("Total wins")

plt.show()
plt.close()
plt.savefig("moveReward.png")

