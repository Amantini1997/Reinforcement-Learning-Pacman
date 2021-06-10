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
    small_wins = split_data(small)
    medium_wins = split_data(medium)

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
#0.8
plot_wins(
    "Win, Win, Win, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Win, Win, Loss, Loss, Loss, Win, Win, Win, Win, Win, Loss, Win, Loss, Loss, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Loss, Loss, Loss, Win, Loss, Loss, Win, Win, Loss, Win, Win, Loss, Win, Loss, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Loss, Loss, Win, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Loss, Loss, Win, Win, Loss, Loss, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Loss, Win, Win, Loss, Win, Win, Loss, Win, Loss, Win, Win, Win, Loss, Loss, Loss, Loss, Win, Win, Loss, Loss, Win, Win",
    "Win, Loss, Loss, Loss, Win, Loss, Win, Win, Loss, Win, Loss, Loss, Loss, Win, Loss, Loss, Loss, Win, Win, Loss, Win, Loss, Loss, Win, Loss, Loss, Loss, Loss, Win, Win, Loss, Win, Loss, Loss, Win, Win, Win, Win, Loss, Loss, Win, Win, Loss, Loss, Win, Win, Win, Loss, Win, Loss, Win, Win, Win, Win, Loss, Loss, Loss, Loss, Win, Loss, Loss, Loss, Win, Win, Win, Loss, Win, Loss, Loss, Loss, Loss, Win, Loss, Win, Loss, Loss, Win, Loss, Win, Win, Loss, Loss, Loss, Win, Win, Loss, Win, Win, Loss, Loss, Win, Loss, Win, Win, Loss, Win, Win, Loss, Loss, Loss, Loss, Win, Loss, Win, Loss, Loss, Loss, Loss, Loss, Loss, Loss, Win, Loss, Win, Win, Win, Loss, Win, Win, Loss, Win, Loss, Loss, Loss, Loss",
    "b")

#0.95
plot_wins(
    "Win, Win, Win, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Loss, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Win, Win, Loss, Win, Loss, Loss, Win, Win, Loss, Win, Win, Win, Win, Loss, Win, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Loss, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Loss, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Loss, Win, Win, Loss, Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Win, Win, Win, Win, Win", 
    "Win, Loss, Win, Loss, Win, Win, Win, Loss, Win, Loss, Win, Loss, Win, Win, Win, Loss, Win, Win, Loss, Loss, Loss, Loss, Loss, Loss, Loss, Win, Loss, Loss, Loss, Win, Win, Win, Loss, Loss, Win, Win, Win, Loss, Win, Loss, Win, Loss, Loss, Win, Loss, Win, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Loss, Win, Win, Loss, Loss, Loss, Win, Win, Loss, Loss, Win, Win, Win, Win, Loss, Loss, Win, Win, Loss, Loss, Loss, Loss, Loss, Loss, Win, Loss, Loss, Win, Win, Win, Win, Loss, Win, Loss, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Loss, Loss, Win, Loss, Loss, Loss, Win, Loss, Win, Win, Loss, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Win, Win, Win, Loss, Loss, Win",
    "g")

#1.00
plot_wins(
    "Loss, Win, Loss, Win, Loss, Win, Loss, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Win, Loss, Loss, Loss, Loss, Win, Loss, Win, Win, Win, Win, Win, Loss, Loss, Win, Win, Win, Win, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Win, Win, Loss, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Win, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Loss, Loss, Win, Win, Win, Loss, Win, Win, Win, Win, Win, Loss, Loss, Win, Win, Win",
    "Loss, Loss, Loss, Loss, Win, Loss, Loss, Win, Loss, Loss, Win, Win, Loss, Loss, Loss, Win, Win, Win, Win, Loss, Loss, Win, Loss, Win, Loss, Loss, Loss, Win, Loss, Win, Loss, Loss, Loss, Loss, Loss, Loss, Win, Win, Win, Loss, Loss, Win, Win, Loss, Win, Win, Win, Win, Win, Win, Win, Loss, Win, Loss, Win, Loss, Loss, Win, Win, Loss, Loss, Loss, Loss, Loss, Win, Win, Loss, Win, Loss, Loss, Win, Win, Win, Win, Win, Win, Loss, Win, Win, Loss, Loss, Loss, Loss, Win, Win, Loss, Win, Win, Win, Loss, Win, Win, Loss, Loss, Win, Loss, Loss, Win, Win, Loss, Loss, Win, Win, Loss, Loss, Loss, Loss, Win, Win, Loss, Loss, Win, Win, Win, Loss, Win, Loss, Loss, Win, Win, Win, Loss, Loss, Loss, Loss",
    "r")

variable = "$\gamma$"

blue = mpatches.Patch(color='b', label=variable+'0.80')
black = mpatches.Patch(color='g', label=variable+'0.95')
red = mpatches.Patch(color='r', label=variable+'1.00')
plt.legend(handles=[blue, black, red])

plt.xlabel("Run count")
plt.ylabel("Total wins")

plt.show()
plt.close()
plt.savefig("gamma.png")

