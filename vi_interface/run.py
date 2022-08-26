import os
import pytest
if __name__ == '__main__':
    # pytest.main()
    pytest.main(args=['-vs', "-x"])
    os.system("allure generate ./temp -o ./reports --clean")
