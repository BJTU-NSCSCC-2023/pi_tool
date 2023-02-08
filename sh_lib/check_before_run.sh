test "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" || echo -e "\033[31mCannot find spear. Check if NSCSCC2023_BJTU_PI_TOOL_HOME set properly.\033[m" || exit 1

piRoot="${NSCSCC2023_BJTU_PI_TOOL_HOME}"

source "${piRoot}/sh_lib/decorator.sh"

echo -e "${begin_c}Checking your running env...${nc_c}"

# Check if conda is installed
condaVersion="$(conda --version)"
if [[ "${condaVersion}" =~ "conda *" ]];then
	echo -e "${pass_c}conda found! Version: [${condaVersion}]${nc_c}"
else
	echo -e "${error_c}Can't find conda!${nc_c}"
	exit 1
fi

# Check if conda env nscscc2023-bjtu-pyenv exists
pyEnvInfo="$(conda env list | grep nscscc2023-bjtu-pyenv)"
if [ -n "${pyEnvInfo}" ];then
	echo -e "${pass_c}Found nscscc2023-bjtu-pyenv on [${pyEnvInfo}].${nc_c}"
else
	echo -e "${error_c}Can't find nscscc2023-bjtu-pyenv !${nc_c}"
	exit 1
fi

function find_bin(){
	local binName=$1
	# echo -e "${message_c}Finding ${binName}...${nc_c}"
	binPath="$(which "${binName}")"
	if [ ! -x "${binPath}" ];then
	   echo -e "${error_c}Cannot find executable ${binName}! Output of \`which ${binName}\`: [${binPath}]${nc_c}"
	   exit 1
	else
	   echo -e "${pass_c}Found ${binName} on [${binPath}]!${nc_c}"
	fi
	export ${binName}Path=${binPath}
}
find_bin sbt
find_bin conan
find_bin wavedrompy
unset -f find_bin

echo -e "${fin_c}Check all passed!${nc_c}"

py="conda run -n nscscc2023-bjtu-pyenv python3"

