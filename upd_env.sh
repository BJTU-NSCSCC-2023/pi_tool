test "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" || echo -e "\033[31mCannot find spear. Check if NSCSCC2023_BJTU_PI_TOOL_HOME set properly.\033[m" || exit 1
source "${NSCSCC2023_BJTU_PI_TOOL_HOME}/sh_lib/check_before_run.sh"

echo -e "${begin_c}Updating your env...${nc_c}"

# for conda env
condaYamlFilePath="${piRoot}/nscscc2023-bjtu-pyenv.yaml"
if [ ! -f "${condaYamlFilePath}" ];then
	echo -e "${error_c}Can't find pyenv yaml file.${nc_c}"
	exit 1
fi
if [ -n "$(conda env list | grep nscscc2023-bjtu-pyenv)" ];then
	echo -e "${message_c}Found nscscc2023-bjtu-pyenv conda env, updating it...${nc_c}"
else
	echo -e "${message_c}Can't find nscscc2023-bjtu-pyenv conda env, creating it...${nc_c}"
fi
conda env update -n nscscc2023-bjtu-pyenv -f "${condaYamlFilePath}"
if [ "$?" -ne "0" ];then
	echo "${error_c}conda env create/update failed.${nc_c}"
	exit 1
fi

# all is done
echo -e "${fin_c}All is done! Wish you a good time!${nc_c}"
