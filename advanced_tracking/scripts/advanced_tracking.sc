global_DATA_PATH = 'advanced_tracking/';

load_trackers(path) ->(global_trackers = read_file(path + 'trackers', 'shared_json'););

load_data(path) ->(
    if(slice(path, length(path)-1) != '/', path += '/');
    global_tracking_data = {};
    file_lst = list_files(path, 'shared_json');
    print(file_lst);
    for(file_lst, (
        path = _;
        player_uuid = slice(_, length(path));
        global_tracking_data:player_uuid = read_file(path, 'shared_json');
    ));
);

save_data(path, players=null) -> (
    if(players==null, players = global_tracking_data);
    if(slice(path, length(path)-1) != '/', path += '/');
    for(players, (
        uuid=_;
        write_file(path+uuid, 'shared_json', global_tracking_data:uuid)
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
    print(pos);
    print(area);
    [x, y, z] = pos;
    if(area:'x_min' != null, if(area:'x_min' > x, return(false)));
    if(area:'x_max' != null, if(area:'x_max' < x, return(false)));
    
    if(area:'y_min' != null, if(area:'y_min' > y, return(false)));
    if(area:'y_max' != null, if(area:'y_max' < y, return(false)));
    
    if(area:'z_min' != null, if(area:'z_min' > z, return(false)));
    if(area:'z_max' != null, if(area:'z_max' < z, return(false)));
    print(true);
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

__on_player_breaks_block(player, block)-> (
    //iterate through groups
    for(global_trackers:'player_break_blocks', (
        group = global_trackers:'player_break_blocks':_;
        print('group ' + group);
        if(!check_player_in_area(player~'pos', group:'area'), continue());
        // print('group area check passed');
        for(group:'components', (
            tracker = _;
            print(tracker);
            if(check_block_interaction_match_tracker(tracker, player, block), print('valid'));
        ))
    ));
)