# Loading Packages ----
for (i in c('dplyr','ggplot2', 'ggpmisc', 'ggpp')){
  if(!(require(i, character.only = TRUE))){
    install.packages(i)
    require(i, character.only = TRUE)}
}

packageVersion("ggpmisc")
# Runtimes with Length ConfLabStudio (M1) ---- 
'''
# Running command: 
# conflab_batch 
# input_path.fasta 
# output_path
# --num-seeds 1
# --model-type auto
# --num-recycle 1 
# --recycle-early-stop-tolerance 0.0 
# --msa-mode mmseqs2_uniref 
# --max-msa 256:256 
# --pair-mode unpaired_paired 
# --rank auto 
# --num-relax 0 
# --num-model 5 
# --num-ensemble 1 
# --templates 
# --zip 
# --model-order 1,2,3,4,5 
# --disable-cluster-profile

run_times_conflabstudio = data.frame(protein = rep(c("Cytochrom C", "GFP", "AKT1", "DNA Topoisomerase 1", "SHIP1", "BRACA1"), each = 5),
                                     length = rep(c(105, 238, 480, 765, 1189, 1863), each = 5),
                                     model = rep(c("model1", "model2", "model3", "model4", "model5"), times = 6),
                                     time_per_model = c(175.3, 167.3, 167.8, 161.9, 161.7, 
                                                        650.7, 641.4, 620.5, 612.6, 611.2,
                                                        2621, 2667.5, 2441.6, 2374.5, 2370.3,
                                                        6717.2, 6705.9, 6007.6, 6006.7, 6101.1,
                                                        20684.7, 20599.8, 18198.6, 18156.7, 18568.5,
                                                        NA, NA, NA, NA, NA
                                                        )
                                     )
run_times_conflabstudio$protein <- factor(run_times_conflabstudio$protein,
                                          levels = unique(run_times_conflabstudio$protein[order(run_times_conflabstudio$length)])
                                          )
(3.71192241871+4.02796987859)/2

nls_test_run_times_conflabstudio = nls((time_per_model/60) ~ a * length^b, data = run_times_conflabstudio, start = list(a = 0.0001888, b = 1.9936569))
summary(nls_test_run_times_conflabstudio)
coefficients_nls_test_run_times_conflabstudio = coef(nls_test_run_times_conflabstudio)
nls_test_run_times_conflabstudio_a <- signif(coefficients_nls_test_run_times_conflabstudio["a"], 3)
nls_test_run_times_conflabstudio_b <- signif(coefficients_nls_test_run_times_conflabstudio["b"], 3)
equation_nls_test_run_times_conflabstudio = paste0("y = ", nls_test_run_times_conflabstudio_a, " * x^", nls_test_run_times_conflabstudio_b)
equation_nls_test_run_times_conflabstudio
ggplot(data = run_times_conflabstudio, 
       aes(length, time_per_model/60/60, color = protein)) +
  geom_smooth(method = "nls",formula = y ~ a * x^b, method.args = list(start = as.list(coefficients_nls_test_run_times_conflabstudio)), se = FALSE, color = "grey60") +
  scale_color_manual(values = c("Cytochrom C" = "darkgoldenrod1",
                               "GFP" = "chartreuse3",
                               "AKT1" = "brown3",
                               "DNA Topoisomerase 1" = "dodgerblue3",
                               "SHIP1" = "deepskyblue",
                               "BRACA1" = "hotpink2")) +
  geom_point() +
  annotate("text", 
           x = max(run_times_conflabstudio$length, na.rm = TRUE) * 0.2,
           y = max(run_times_conflabstudio$time_per_model/60/60, na.rm = TRUE) *0.8,
           label = equation_nls_test_run_times_conflabstudio) +
  labs(title = "Average Runtime per Model by Sequence Length",
       x = "Length [aa]",
       y = "Runtime [h]",
       color = "Protein")
'''
# Runtimes with Length ConfLabStudio (M1) excluding BRACA1 ----

run_times_conflabstudio = data.frame(protein = rep(c("Cytochrom C", "GFP", "AKT1", "DNA Topoisomerase 1", "SHIP1"), each = 5),
                                     length = rep(c(105, 238, 480, 765, 1189), each = 5),
                                     model = rep(c("model1", "model2", "model3", "model4", "model5"), times = 5),
                                     time_per_model = c(175.3, 167.3, 167.8, 161.9, 161.7, 
                                                        650.7, 641.4, 620.5, 612.6, 611.2,
                                                        2621, 2667.5, 2441.6, 2374.5, 2370.3,
                                                        6717.2, 6705.9, 6007.6, 6006.7, 6101.1,
                                                        20684.7, 20599.8, 18198.6, 18156.7, 18568.5
                                     )
)
run_times_conflabstudio$protein <- factor(run_times_conflabstudio$protein,
                                          levels = unique(run_times_conflabstudio$protein[order(run_times_conflabstudio$length)])
)
(3.71192241871+4.02796987859)/2

nls_test_run_times_conflabstudio = nls((time_per_model/60) ~ a * length^b, data = run_times_conflabstudio, start = list(a = 0.0001888, b = 1.9936569))
summary(nls_test_run_times_conflabstudio)
coefficients_nls_test_run_times_conflabstudio = coef(nls_test_run_times_conflabstudio)
nls_test_run_times_conflabstudio_a <- signif(coefficients_nls_test_run_times_conflabstudio["a"], 3)
nls_test_run_times_conflabstudio_b <- signif(coefficients_nls_test_run_times_conflabstudio["b"], 3)
equation_nls_test_run_times_conflabstudio = paste0("y = ", nls_test_run_times_conflabstudio_a, " * x^", nls_test_run_times_conflabstudio_b)
equation_nls_test_run_times_conflabstudio
ggplot(data = run_times_conflabstudio, 
       aes(length, time_per_model/60/60, color = protein)) +
  geom_smooth(method = "nls",formula = y ~ a * x^b, method.args = list(start = as.list(coefficients_nls_test_run_times_conflabstudio)), se = FALSE, color = "grey60") +
  scale_color_manual(values = c("Cytochrom C" = "darkgoldenrod1",
                                "GFP" = "chartreuse3",
                                "AKT1" = "darkred",
                                "DNA Topoisomerase 1" = "dodgerblue3",
                                "SHIP1" = "deepskyblue")) +
  geom_point() +
  geom_vline(xintercept = 270,
             linetype = "dashed",
             color = "darkgreen") +
  geom_vline(xintercept = 242,
             linetype = "dashed",
             color = "purple") +
  geom_vline(xintercept = 353,
             linetype = "dashed",
             color = "maroon") +
  annotate("text", x = 270, y = max(run_times_conflabstudio$time_per_model/60/60, na.rm = TRUE) * 0.70,
           label = "mean protein length bacteria", angle = 90, vjust = -0.4, size = 3,
           color = "darkgreen") +
  annotate("text", x = 242, y = max(run_times_conflabstudio$time_per_model/60/60, na.rm = TRUE) * 0.70,
           label = "mean protein lengh archaea", angle = 90, vjust = -0.4, size = 3,
           color = "purple") +
  annotate("text", x = 353, y = max(run_times_conflabstudio$time_per_model/60/60, na.rm = TRUE) * 0.70,
           label = "mean protein length eucarya", angle = 90, vjust = -0.4, size = 3,
           color = "maroon") +
  annotate("text", 
           x = max(run_times_conflabstudio$length, na.rm = TRUE) * 0.7,
           y = max(run_times_conflabstudio$time_per_model/60/60, na.rm = TRUE) *0.8,
           label = equation_nls_test_run_times_conflabstudio) +
  labs(title = "Average Runtime per Model by Sequence Length",
       x = "Length [aa]",
       y = "Runtime [h]",
       color = "Protein")


# Runtimes with Recycles ConfLabStudio (M1) Tc5b ----
'''
# Running command: 
# conflab_batch 
# input_path.fasta 
# output_path
# --num-seeds 1
# --model-type auto
# --num-recycle 1-5
# --recycle-early-stop-tolerance 0.0 
# --msa-mode mmseqs2_uniref 
# --max-msa 256:256 
# --pair-mode unpaired_paired 
# --rank auto 
# --num-relax 0 
# --num-model 5 
# --num-ensemble 1 
# --templates 
# --zip 
# --model-order 1,2,3,4,5 
# --disable-cluster-profile


recycles_conflabstudio = data.frame(protein = rep(c("TC5b"), each = 6),
                                    length = rep(c(20), each =6),
                                    num_recycles = c(0,1,2,3,4,5),
                                    total_duration_s = c(23, 26, 28, 32, 34, 35),
                                    rank1_pLDDT = c(NA, NA, NA, NA, NA, NA)
                                    )

recycles_conflabstudio$protein <- factor(recycles_conflabstudio$protein,
                                          levels = unique(recycles_conflabstudio$protein[order(recycles_conflabstudio$length)])
)

ggplot(recycles_conflabstudio,
       aes(num_recycles, total_duration_s, color = protein)) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_color_manual(values = c("TC5b" = "mediumpurple1")) +
  geom_point() +
  stat_poly_eq(formula = y ~ x,
               aes(label = paste(
                 ..eq.label..,
                 ..rr.label..,
                 ..p.value.label..,
                 sep = "~~~"),
                 group = protein,
                 color = protein),
               label.x.npc = "left",
               label.y.npc = "top") +
  labs(title = "Correlation Between Total Duration and Number of Recycles",
       x = "Number of Recycles",
       y = "Total Duration [s]",
       color = "Protein"
       )
'''
# Runtimes with Recycles ConfLabStudio (M1) ----
recycles_conflabstudio = data.frame(protein = rep(c("Cytochrom C", "GFP", "AKT1"), each = 6),
                                    length = rep(c(105, 238, 480), each = 6),
                                    num_recycles = rep(c(0,1,2,3,4,5), times = 3),
                                    total_duration_s = c(342, 658, 975, 1291, 1623, 1880,
                                                         1615, 3442, 4782, 6312, 7887, 9430,
                                                         6352, 12368, 18476, 25046, 30808, 36878),
                                    device = c(c(rep("M3"), times = 6),
                                               c(rep("M1"), times = 6),
                                               c(rep("M1"), times = 6)
                                               )
                                    )

recycles_conflabstudio$total_duration_rel <- with(recycles_conflabstudio,
                                                  total_duration_s / ave(total_duration_s, protein, FUN = function(x) x[1])
                                                  )
recycles_conflabstudio$protein <- factor(recycles_conflabstudio$protein,
                                         levels = unique(recycles_conflabstudio$protein[order(recycles_conflabstudio$length)])
)
recycles_conflabstudio

summary(lm(total_duration_s ~ num_recycles, data = subset(recycles_conflabstudio, protein == "Cytochrom C")))
summary(lm(total_duration_s ~ num_recycles, data = subset(recycles_conflabstudio, protein == "GFP")))
summary(lm(total_duration_s ~ num_recycles, data = subset(recycles_conflabstudio, protein == "AKT1")))

ggplot(recycles_conflabstudio,
       aes(num_recycles, total_duration_rel, color = protein)) +
  geom_smooth(method = "lm", se = FALSE, na.rm = TRUE) +
  scale_color_manual(values = c("Cytochrom C" = "darkgoldenrod1",
                                "GFP" = "chartreuse3",
                                "AKT1" = "brown3")) +
  geom_point(na.rm = TRUE) +
  stat_poly_eq(formula = y ~ x,
               aes(label = paste(after_stat(eq.label),
                                 after_stat(rr.label),
                                 after_stat(p.value.label),
                                 sep = "~~~"),
                   group = protein,
                   color = protein),
               parse = TRUE,
               small.p = TRUE,
               rsquared.conf.level = NA) +
  labs(title = "Correlation Between Number of Recycles and Total Modeling Duration",
       x = "Number of Recycles",
       y = "Relative Total Runtime",
       color = "Protein"
       )
