CARPET_SCRIPT = """global_DATA_PATH = 'advanced_tracking/';


// Tracking System

load_trackers(path) ->(
    if(slice(path, length(path)-1) != '/', path += '/');
    global_trackers = read_file(path + 'trackers', 'shared_json');
);

load_data(path) ->(
    if(slice(path, length(path)-1) != '/', path += '/');
    global_tracking_data = {};
    data_path = path + 'tracked_data/';
    file_lst = list_files(data_path, 'shared_json');
    // print(file_lst);
    for(file_lst, (
        player_file_path = _;
        player_uuid = slice(player_file_path, length(data_path));
        // print(player_file_path);
        // print(length(data_path));
        // print(player_uuid);
        global_tracking_data:player_uuid = read_file(player_file_path, 'shared_json');
    ));
);

save_data(path, players=null) -> (
    if(slice(path, length(path)-1) != '/', path += '/');
    data_path = path + 'tracked_data/';
    if(players==null, players = global_tracking_data);
    for(players, (
        uuid=_~'uuid';
        // print('saving + '+uuid);
        write_file(data_path+uuid, 'shared_json', global_tracking_data:uuid)
    ));
);

check_block_in_list(block, list) -> (
    // print(block);
    // print(list);
    if(list~(block+'')==null, return(false));
    requirements = list:(block+'');
    for(requirements, (
        requirement = _;
        flag = true;
        for(requirement, (
            if(block_state(block, _) != requirement:_, (flag=false; break()));
        ));
        if(flag, return(true));
    ));
    return(false);
);

check_player_in_area(pos, area) -> (
    // print(pos);
    // print(area);
    [x, y, z] = pos;
    if(area:'x_min' != null, if(area:'x_min' > x, return(false)));
    if(area:'x_max' != null, if(area:'x_max' < x, return(false)));
    
    if(area:'y_min' != null, if(area:'y_min' > y, return(false)));
    if(area:'y_max' != null, if(area:'y_max' < y, return(false)));
    
    if(area:'z_min' != null, if(area:'z_min' > z, return(false)));
    if(area:'z_max' != null, if(area:'z_max' < z, return(false)));
    // print(true);
    return(true);
);

check_block_interaction_match_component(component, player, block) -> (
    // check area
    if(!check_player_in_area(player~'pos', component:'area'), return(false));
    
    block_type_restrictions = component:'block_type';

    if(block_type_restrictions:'mode'=='whitelist', if(check_block_in_list(block, block_type_restrictions:'list')==false, return(false)));
    if(block_type_restrictions:'mode'=='blacklist', if(check_block_in_list(block, block_type_restrictions:'list'), return(false)));

    return(true);
);

increment_tracker(tracker_name, player) -> (
    // global_tracking_data:(player ~ 'uuid'):'trackers':tracker_name += 1;
    print(player ~ 'uuid');
    print(global_tracking_data:(player ~ 'uuid'));
    global_tracking_data:(player ~ 'uuid'):'trackers':tracker_name += 1;
    save_data(global_DATA_PATH, [player]);
);

update_block_tracker(player, block, tracker_type) -> (
    //iterate through groups
    for(global_trackers:tracker_type, (
        group = global_trackers:tracker_type:_;
        // print('group ' + group);
        if(!check_player_in_area(player~'pos', group:'area'), continue());
        // print('group area check passed');
        for(group:'trackers', (
            tracker_id = _;
            tracker = group:'trackers':tracker_id;
            // print(tracker);
            if(!check_player_in_area(player~'pos', tracker:'area'), continue());
            for(tracker:'components', (
                component = tracker:'components':_;
                if(check_block_interaction_match_component(component, player, block), (
                    increment_tracker(tracker_id, player);
                    update_scoreboards(tracker:'scoreboards', player);
                    if(tracker:'mode' == 'union', break);
                ));
            ))
        ))
    ));
);

check_player_profile(player, path=null) -> (
    if(path==null, path = global_DATA_PATH);
    if(slice(path, length(path)-1) != '/', path += '/');
    data_path = path + 'tracked_data/';
    if(list_files(data_path, 'shared_json') ~ (data_path + player~'uuid') == null, (
        write_file(data_path + (player~'uuid'), 'shared_json', {'player_ID'-> player, 'trackers'->{}});
        global_tracking_data:(player~'uuid') = {'player_ID'-> player, 'trackers'->{}}
    ), 
    globa_tracking_data:(player~'uuid'):'player_ID' = player;
    )
);


// Scoreboard System
load_scoreboard(objective, display) -> (
    print('objective ' + objective);
    print('display_name ' + display);
    if(scoreboard()~objective == null, scoreboard_add(objective));
    scoreboard_property(objective, 'display_name', display)
);

load_scoreboards(path) -> (
    if(slice(path, length(path)-1) != '/', path += '/');
    global_scoreboards = read_file(path + 'scoreboards', 'shared_json');
    //initialize and update displaynames for objectives
    for(global_scoreboards, (
        objective = _;
        display = global_scoreboards:objective:'display_name';
        load_scoreboard(objective, display);
    ))
);

update_scoreboard(objective, player) -> (
    // print(objective);
    // print(player);
    scoreboard_config = global_scoreboards:objective;
    if(scoreboard_config:'mode' == 'weighted_sum', (
        acc=0.0;
        for(scoreboard_config:'trackers', (
            tracker = _;
            tracker_id=tracker:'tracker_id';
            weight = tracker:'weight';
            // print(tracker_id);
            // print(weight);
            acc += (global_tracking_data:(player ~ 'uuid'):'trackers':tracker_id)*weight;
        ));
        scoreboard(objective, player, acc)
    ))
    
);

update_scoreboards(objectives, player) -> (
    for(objectives, update_scoreboard(_, player))
);


__on_start() -> (
    load_trackers(global_DATA_PATH);
    load_data(global_DATA_PATH);
    load_scoreboards(global_DATA_PATH);
    for(player('all'), check_player_profile(_, global_DATA_PATH))
);

__on_player_breaks_block(player, block)-> (
    update_block_tracker(player, block, 'player_break_blocks');
);

__on_player_places_block(player, item_tuple, hand, block)->(
    update_block_tracker(player, block, 'player_place_blocks');
);

__on_player_connects(player)-> (
    check_player_profile(player, global_DATA_PATH);
);"""