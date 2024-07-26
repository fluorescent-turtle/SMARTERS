"""#todo: devi restaurare questo codice, perche' la dimensione della griglia varia se creata o random,

def create_environment(
    data_e,
    dim_tassel,
    env_plugins,
    grid_width,
    grid_height,
    created,
):

    grid, resources = initialize_grid_and_resources(grid_width, grid_height)

    try:
        if not created:
            raw_shapes = data_e["circles"] + data_e["squares"] + data_e["isolated_area"]
            grid, resources = initialize_grid_and_resources(int(data_e["width"]), int(data_e["length"]))
            corner, blocked_tassels = create_grid(
                "default",
                data_e,
                grid_width,
                grid_height,
                dim_tassel,
                raw_shapes,
                grid,
            )
            created = True
            return grid, corner, created, blocked_tassels
    except Exception:
        grid, resources = initialize_grid_and_resources(grid_width, grid_height)
        corner, blocked_tassels = create_grid(
            "random",
            data_e,
            grid_width,
            grid_height,
            dim_tassel,
            resources,
            grid,
        )
        if corner is None:
            if env_plugins:
                grid, corner = execute_plugins(
                    env_plugins, grid, grid_width, grid_height
                )

        return grid, corner, created, blocked_tassels







def runner(
    robot_plugin,
    grid,
    cycles,
    base_station_pos,
    data_r,
    grid_width,
    grid_height,
    i,
    j,
    cycle_data,
    filename,
    dim_tassel,
):
    movement_type, boing = split_at_first_hyphen(data_r["cutting_mode"])

    plugin = (
        robot_plugin(grid, base_station_pos)
        if robot_plugin
        else DefaultMovementPlugin(
            movement_type=movement_type,
            grid=grid,
            base_station_pos=base_station_pos,
            boing=boing,
            cut_diameter=data_r["cutting_diameter"],
            grid_width=grid_width,
            grid_height=grid_height,
            dim_tassel=dim_tassel,
        )
    )

    # Process the grid data and save it to a CSV file
    process_grid_data(grid_height, grid_width, i, j, filename, dim_tassel, grid)

    current_data = []
    Simulator(
        grid,
        cycles,
        base_station_pos,
        plugin,
        data_r["speed"],
        data_r["autonomy"] - (data_r["autonomy"] / 10),
        i,
        j,
        current_data,
        filename,
        dim_tassel,
    ).step()
    cycle_data.append(current_data)





def run_model_with_parameters(env_plugins, robot_plugin):

    # Load setup data from the file
    data_r, data_e, data_s = load_data_from_file("../SetUp/data_file")
    repetitions = data_s["repetitions"]
    num_maps = data_s["num_maps"]

    # Calculate the number of cycles in seconds
    cycles = data_s["cycle"] * 3600
    dim_tassel = data_s["dim_tassel"]
    grid_width = math.ceil(data_e["width"] / dim_tassel)
    grid_height = math.ceil(data_e["length"] / dim_tassel)
    created = False

    for i in range(num_maps):
        cycle_data = []
        grid, random_corner, created, biggest_area_blocked = create_environment(
            data_e,
            dim_tassel,
            env_plugins,
            grid_width,
            grid_height,
            created,
        )

        # Process the grid data and save it
        process_grid_data(
            grid_height,
            grid_width,
            i,
            0,
            f"grid{get_current_datetime()}.csv",
            dim_tassel,
            grid,
        )

        # Populate perimeter guidelines in the grid
        populate_perimeter_guidelines(grid_width, grid_height, grid, dim_tassel)

        # Create deep copies of the grid for different strategies
        grid1 = copy.deepcopy(grid)
        grid2 = copy.deepcopy(grid)
        grid3 = copy.deepcopy(grid)

        for j in range(repetitions):
            # Place the base station using the perimeter pair strategy
            base_station_pos = put_station_guidelines(
                PerimeterPairStrategy,
                grid1,
                grid_width,
                grid_height,
                random_corner,
                None,
                biggest_area_blocked,
            )

            if base_station_pos is not None:
                runner(
                    robot_plugin,
                    grid1,
                    cycles,
                    base_station_pos,
                    data_r,
                    grid_width,
                    grid_height,
                    i,
                    j,
                    cycle_data,
                    f"perimeter_model{get_current_datetime()}.csv",
                    dim_tassel,
                )

            if biggest_area_blocked:
                # Place the base station using the biggest random pair strategy
                base_station_pos = put_station_guidelines(
                    BiggestRandomPairStrategy,
                    grid2,
                    grid_width,
                    grid_height,
                    random_corner,
                    None,
                    biggest_area_blocked,
                )

                if base_station_pos is not None:
                    runner(
                        robot_plugin,
                        grid2,
                        cycles,
                        base_station_pos,
                        data_r,
                        grid_width,
                        grid_height,
                        i,
                        j,
                        cycle_data,
                        f"big_model{get_current_datetime()}.csv",
                        dim_tassel,
                    )

                # Find the central tassel position
                central_tassel = find_central_tassel(grid_width, grid_height)

                # Place the base station using the biggest center pair strategy
                base_station_pos = put_station_guidelines(
                    BiggestCenterPairStrategy,
                    grid3,
                    grid_width,
                    grid_height,
                    random_corner,
                    central_tassel,
                    biggest_area_blocked,
                )

                if base_station_pos is not None:
                    runner(
                        robot_plugin,
                        grid3,
                        cycles,
                        base_station_pos,
                        data_r,
                        grid_width,
                        grid_height,
                        i,
                        j,
                        cycle_data,
                        f"bigcenter_model{get_current_datetime()}.csv",
                        dim_tassel,
                    )"""
