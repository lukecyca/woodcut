THIS_PATH="${BASH_SOURCE[0]}";
if([ -h "${THIS_PATH}" ]) then
  while([ -h "${THIS_PATH}" ]) do THIS_PATH=`readlink "${THIS_PATH}"`; done
fi
pushd . > /dev/null
cd `dirname ${THIS_PATH}` > /dev/null
THIS_PATH=`pwd`;
popd  > /dev/null

export PYTHONPATH=$THIS_PATH:$PYTHONPATH
export PATH=$THIS_PATH/bin:$PATH
