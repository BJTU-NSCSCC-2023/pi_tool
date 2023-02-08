test "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" || echo -e "\033[31mCannot find spear. Check if NSCSCC2023_BJTU_PI_TOOL_HOME set properly.\033[m" || exit 1

source ${NSCSCC2023_BJTU_PI_TOOL_HOME}/sh_lib/check_before_run.sh

echo -e "${begin_c}Updating your env...${nc_c}"

echo -e "${message_c}Dumping conda env yaml.${nc_c}"
conda env export -n nscscc2023-bjtu-pyenv --file "${piRoot}/nscscc2023-bjtu-pyenv.yaml"
sed -i '/^prefix:/d' "${piRoot}/nscscc2023-bjtu-pyenv.yaml"

echo -e "${fin_c}Finished.${nc_c}"
