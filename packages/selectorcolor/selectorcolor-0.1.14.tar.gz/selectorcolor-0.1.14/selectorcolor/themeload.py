import flet as ft
from os import path
from pickle import dump, load

class ThemeLoad(ft.Container):
    def __init__(self, tema, layout,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = layout
        self.adicionados = {}

        self.GetArquivo(tema)
        self.tema_escolhido = ft.Dropdown(
            hint_text='Selecione um tema',
            hint_style=ft.TextStyle(color='grey300'),         
            width=1500,
            max_menu_height =  300,
            dense=True,
            filled=True,
            fill_color='grey900', 
            border_color='grey800',
            border_radius=15, 
            border_width=1,
            col ={'xs':12, 'sm':8},
            expand=True,         
            
            options = [
                ft.dropdown.Option(i)
                for i in sorted(list(self.arquiv.keys()))
            ],
            on_change=self.CarregarTema
        )
        self.content = self.tema_escolhido

  
    def GetArquivo(self, caminho = None):        
        self.nome_temas = path.join(path.dirname(path.abspath(__file__)), 'Temas.plk')
        caminho = caminho if caminho else self.nome_temas
        self.arquiv = self.LerPickle(caminho) or  {  "black": {
                "Container": "#226076",
                "Fundo": "#1C1E1F",
                "Texto":" #8CC34B",
                "Título": "#2DA860",
                "Texto 1": "#9CA678",
                "Texto 2": "#D9E1E4",
                "Bordas": "#1B232D",
                "Sombras": "#1B232D",
                "Gradiente": "#166A7A",
                "Botão":"#352D4C",
                "primary":  "#CAD0E8",
                "on_primary":  None,
                "on_secondary_container":  None,
                "outline":  None,
                "shadow":  None,
                "on_surface_variant":  None,
                "surface_variant":  None,
                "primary_container":  None,
                "on_surface":  None,
                "surface":  None,
                "secondary": None,
                "error":None,
                "scrim": None,
                "tertiary": None
                
            }
        }
      

    def set_attrs(self, obj, attr_path, value):
        # Divida o caminho do atributo em uma lista
        attrs = attr_path.split('.')
        
        # Itere até o penúltimo atributo
        for attr in attrs[:-1]:
            obj = getattr(obj, attr)
        
        # Verifique se o último atributo é um índice de lista
        final_attr = attrs[-1]
        if '[' in final_attr and ']' in final_attr:
            # Obtenha o nome do atributo da lista e o índice
            list_attr = final_attr.split('[')[0]
            index = int(final_attr.split('[')[1].split(']')[0])
            
            # Defina o valor no índice específico da lista
            getattr(obj, list_attr)[index] = value
        else:
            # Defina o valor no atributo final
            setattr(obj, final_attr, value)        


    def AddAtriburColor(self, nome, atributo):
        self.adicionados[nome] = atributo


    def CarregarTema(self, e):
        tema = self.tema_escolhido.value
        if tema:
            dic = self.arquiv[tema].copy()
            self.page.theme = ft.Theme(
                color_scheme= ft.ColorScheme(
                    primary = dic.get("primary"),
                    on_primary = dic.get("on_primary"),
                    on_secondary_container = dic.get("on_secondary_container"),
                    outline = dic.get("outline"),
                    shadow = dic.get("shadow"),
                    on_surface_variant = dic.get("on_surface_variant"),
                    surface_variant = dic.get("surface_variant"),
                    primary_container = dic.get("primary_container"),
                    on_surface = dic.get("on_surface"),
                    secondary = dic.get("secondary"),
                    error = dic.get("error"),
                    scrim = dic.get("scrim"),
                    tertiary = dic.get("tertiary"),
                ),
                text_theme = ft.TextTheme(
                    body_medium=ft.TextStyle(color=dic.get("Texto")),  # Cor do texto padrão
                    body_small=ft.TextStyle(color=dic.get("Texto_boddy_small")) , 
                ),
            #     scrollbar_theme=ft.ScrollbarTheme(
            #         thickness = 10,
            #         cross_axis_margin = -15,
            #         min_thumb_length = 20,
            #         track_color = 'grey500',
            #         thumb_color = 'grey900',
            #     ),

            )
            self.page.bgcolor =  'surface'   

            for i in self.adicionados.keys():
                self.set_attrs(self.layout,self.adicionados[i], dic.get(i, 'black'))
            self.layout.update()
     


            self.update()
            self.page.update()


    def LerPickle(self, nome):
        if path.isfile(nome):
            with open(nome, 'rb') as arquivo:
                return load(arquivo)
        else:
            return None   