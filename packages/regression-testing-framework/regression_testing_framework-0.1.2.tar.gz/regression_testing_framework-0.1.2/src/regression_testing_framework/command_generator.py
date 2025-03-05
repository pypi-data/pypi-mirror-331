import yaml

def generate_commands(config_path):
    """
    Generate command representations for dry-run display.
    These aren't the actual commands that will be executed,
    but rather a representation for the user to understand what will run.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Generate command representations
    commands = []
    global_base_command = config.get('base_command', '/bin/bash')
    
    for test_name, test_config in config.items():
        if test_name == 'base_command':
            continue
        
        if not isinstance(test_config, dict):
            commands.append(f"{test_name}: <Invalid configuration>")
            continue
            
        # Get test-specific base command or use global
        base_command = test_config.get('base_command', global_base_command)
        
        # Build command string
        cmd_parts = [base_command]
        
        # Handle params
        if 'params' in test_config and isinstance(test_config['params'], list):
            for param in test_config['params']:
                if isinstance(param, dict):
                    for key, value in param.items():
                        if key == 'c' and base_command in ['/bin/bash', '/bin/sh', 'bash', 'sh']:
                            cmd_parts.append('-c')
                            cmd_parts.append(f"{value}")
                        elif value is None:
                            cmd_parts.append(f"-{key}")
                        else:
                            cmd_parts.append(f"-{key}")
                            cmd_parts.append(f"{value}")
                elif isinstance(param, str):
                    cmd_parts.append(param)
        
        # Add environment variables if present
        env_str = ""
        if 'environment' in test_config and isinstance(test_config['environment'], list):
            env_str = " [Environment: " + ", ".join(test_config['environment']) + "]"
        
        commands.append(f"{test_name}: {' '.join(cmd_parts)}{env_str}")
    
    return commands
