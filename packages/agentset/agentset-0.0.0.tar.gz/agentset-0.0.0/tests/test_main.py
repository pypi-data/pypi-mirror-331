import pytest
from agentset import print_agentset

def test_print_agentset():
    print_agentset()
    assert print_agentset.__name__ == "print_agentset"

if __name__ == "__main__":
    pytest.main()