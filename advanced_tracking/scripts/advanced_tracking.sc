global_DATA_PATH = 'advanced_tracking/';

load_trackers(path) ->(global_trackers = read_file(path + 'trackers', 'shared_json'););

load_data(path) ->(
    if(slice(path, length(path)-1) != '/', path += '/');
    global_tracking_data = {};
    data_path = path + 'tracked_data/';
    file_lst = list_files(data_path, 'shared_json');
    print(file_lst);
    for(file_lst, (
        player_file_path = _;
        player_uuid = slice(player_file_path, length(data_path));
        print(player_file_path);
        print(length(data_path));
        print(player_uuid);
        global_tracking_data:player_uuid = read_file(player_file_path, 'shared_json');
    ));
);

save_data(path, players=null) -> (
    if(slice(path, length(path)-1) != '/', path += '/');
    data_path = path + 'tracked_data/';
    if(players==null, players = global_tracking_data);
    for(players, (
        uuid=_~'uuid';
        print('saving + '+uuid);
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



check_block_interaction_match_tracker(tracker, player, block) -> (
    // check area
    if(!check_player_in_area(player~'pos', tracker:'area'), return(false));
    
    specs = tracker:'specs';
    block_type_restrictions = specs:'block_type';

    if(block_type_restrictions:'mode'=='whitelist', if(check_block_in_list(block, block_type_restrictions:'whitelist')==false, return(false)));
    if(block_type_restrictions:'mode'=='blacklist', if(check_block_in_list(block, block_type_restrictions:'blacklist'), return(false)));

    return(true);
);


__on_start() -> (
    load_trackers(global_DATA_PATH);
    load_data(global_DATA_PATH);
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
            tracker = _;
            // print(tracker);
            if(check_block_interaction_match_tracker(tracker, player, block), increment_tracker(tracker:'tracker', player));
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

__on_player_breaks_block(player, block)-> (
    update_block_tracker(player, block, 'player_break_blocks')
);

__on_player_connects(player)-> (
    check_player_profile(player, global_DATA_PATH)
)