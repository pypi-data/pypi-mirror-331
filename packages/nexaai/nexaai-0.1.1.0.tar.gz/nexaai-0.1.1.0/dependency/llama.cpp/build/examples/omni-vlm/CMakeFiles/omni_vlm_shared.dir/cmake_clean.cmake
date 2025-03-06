file(REMOVE_RECURSE
  "libomni_vlm_shared.pdb"
  "libomni_vlm_shared.so"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/omni_vlm_shared.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
