"""def _process_cycle_data(self, cycle):
    cycle_data = []

    counts = [["Empty" for i in range(self.grid.width)] for j in range(self.grid.height)]
    for x in range(self.grid.height):
        for y in range(self.grid.width):
            # counts = 0
            contents = []
            for grass_tassel in self.grass_tassels:
                if (
                        (coords := grass_tassel.get())
                        and coords[0] == x
                        and coords[1] == y
                ):
                    counts = grass_tassel.get_counts()
                    contents = self.grid.get_cell_list_contents(coords)
                    break

            data = {
                "num_mappa": self.i,
                "ripetizione": self.j,
                "cycle": cycle,
                "x": x,
                "y": y,
                "counts": counts,
            }

            cycle_data.append(data)
    for grass_tassel in self.grass_tassels:
        print(f"GRASS TASSEL GET: {grass_tassel.get()}")
        x, y = grass_tassel.get()
        print(f"X {x} Y{y} WIDTH: {self.grid.width} HEIGHT: {self.grid.height}")
        counts[x][y] = grass_tassel.get_counts()
    df = pd.DataFrame(counts)
    df = df.rename(columns={j: j * self.dim_tassel for j in range(self.grid.width)})
    df.insert(loc=0, column="num_mappa", value=self.i)
    df.insert(loc=1, column="ripetizione", value=self.j)
    df.insert(loc=2, column="cycle", value=cycle)
    df.insert(loc=3, column="x", value=[self.dim_tassel * i for i in range(self.grid.height)])
    print(f"CYCLE: {cycle}")
    output_dir = os.path.abspath("./View/")

    plt.switch_backend("Agg")

    def reduce_ticks(ticks, step):
        return [tick if i % step == 0 else "" for i, tick in enumerate(ticks)]

    xtick = [j * self.dim_tassel for j in range(self.grid.width)]
    ytick = [i * self.dim_tassel for i in range(self.grid.height)]

    tick_step = 20
    reduced_xtick = reduce_ticks(xtick, tick_step)
    reduced_ytick = reduce_ticks(ytick, tick_step)

    for (num_mappa, ripetizione, group_cycle), group in df.groupby(
            ["num_mappa", "ripetizione", "cycle"]
    ):
        fig, ax = plt.subplots()

        heatmap_data = group.pivot(columns="x", values="counts")
        ax.xaxis.tick_top()
        sns.heatmap(
            heatmap_data,
            annot=False,
            cmap="BuGn",
            cbar_kws={"label": "Counts"},
            xticklabels=reduced_xtick,
            yticklabels=reduced_ytick,
            robust=True,
            vmin=-1,
            ax=ax,
        )

        # Costruire il percorso del file con un formato di data sicuro
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        file_path = os.path.join(output_dir, f"heatmap_{timestamp}.png")

        # Salvare la figura
        plt.savefig(file_path)
        plt.close(fig)  # Chiudere la figura esplicitamente per liberare memoria

    # Salvare i dati su un file CSV
    df.to_csv(os.path.join(output_dir, f"{self.filename}_cycle_{cycle}.csv"), index=False)"""

"""plt.switch_backend("Agg")

        def reduce_ticks(ticks, step):
            return [tick if i % step == 0 else "" for i, tick in enumerate(ticks)]

        xtick = [j * self.dim_tassel for j in range(self.grid.width)]
        ytick = [i * self.dim_tassel for i in range(self.grid.height)]

        tick_step = 20
        reduced_xtick = reduce_ticks(xtick, tick_step)
        reduced_ytick = reduce_ticks(ytick, tick_step)

    for (num_mappa, ripetizione, group_cycle), group in df.groupby(
                ["num_mappa", "ripetizione", "cycle"]
        ):
            fig, ax = plt.subplots()

            heatmap_data = group.pivot(columns="x", index="y", values="counts")
            ax.xaxis.tick_top()
            sns.heatmap(
                heatmap_data,
                annot=False,
                cmap="BuGn",
                cbar_kws={"label": "Counts"},
                xticklabels=reduced_xtick,
                yticklabels=reduced_ytick,
                robust=True,
                vmin=-1,
                ax=ax,
            )"""
