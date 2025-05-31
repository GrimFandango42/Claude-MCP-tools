#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server_fastmcp_fixed import select_optimal_provider, PROVIDERS

test_cases = [
    ('Hello world', 'balanced'),
    ('Analyze this private document', 'privacy'), 
    ('Quick summary needed', 'speed'),
    ('Complex analysis required', 'quality'),
    ('Cheap processing', 'cost')
]

print('Testing AI Routing Logic:')
print('=' * 40)
for prompt, priority in test_cases:
    provider = select_optimal_provider(prompt, priority)
    config = PROVIDERS[provider]
    print(f'Prompt: "{prompt}"')
    print(f'Priority: {priority} -> {provider}')
    print(f'Model: {config.name} ({config.model})')
    cost = 'Free' if config.cost_per_1k_tokens == 0 else f'${config.cost_per_1k_tokens}/1k tokens'
    privacy = 'High (Local)' if config.is_local else 'Low (Cloud)'
    print(f'Cost: {cost}')
    print(f'Privacy: {privacy}')
    print('-' * 40)

print('All routing tests completed successfully!')
