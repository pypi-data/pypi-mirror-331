from sys import path as pthsys
# pthsys.append(r'D:\baixados\programas_python\baixar_do_youtube_final')

import flet as ft
from selectorcolor import SelectorColor

# from pathlib import Path

# Adicione o diretório raiz do projeto ao PATH do Python
# CAMINHO_RAIZ = Path(__file__).parent.parent  # Volta duas pastas (layout -> projeto)

class SaveSelectFile2(ft.ElevatedButton):
    def __init__(self, tipo, nome=None, func = None):
        """
        tipo == path: seleciona uma pasta (retorna o caminho completo da pasta selecionada)
        tipo == file: seleciona um arquivo (retorna o caminho completo do arquivo selecionado)
        tipo == save: salva um arquivo (retorna o caminho completo do arquivo, junto com seu nome)
        """
        super().__init__()
        self.nome = nome if nome else self.default_nome(tipo)
        self.func = func
        self.tipo = tipo
        self.visible = True
        self._value = None
        self.styleyle = ft.ButtonStyle(
            enable_feedback = True
        )
        self.bgcolor='grey800'
        self.color="#B0B3B1"
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        self.style = ft.ButtonStyle(
            text_style=ft.TextStyle(
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        )
        
        self.configurar_botao(tipo)

    def default_nome(self, tipo):
        default_nomes = {
            'file': 'Selecione o arquivo',
            'path': 'Selecione a pasta',
            'save': 'Digite o nome do arquivo',
        }
        return default_nomes.get(tipo, 'Selecionar')

    def configurar_botao(self, tipo):
        icones = {
            'file': ft.Icons.FILE_OPEN,
            'path': ft.Icons.UPLOAD_FILE,
            'save': ft.Icons.SAVE,
        }
        acoes = {
            'file': self.selecionar_arquivo,
            'path': self.selecionar_pasta,
            'save': self.save,
        }
        self.text = self.nome
        self.icon = icones[tipo]
        self.on_click = acoes[tipo]

    async def selecionar_arquivo(self, _):
        self.pick_files_dialog.pick_files(
            allow_multiple=True,
            allowed_extensions = ['plk']
            )

    async def selecionar_pasta(self, _):
        self.pick_files_dialog.get_directory_path()

    async def save(self, _):
        self.pick_files_dialog.save_file()

    async def pick_files_result(self, e: ft.FilePickerResultEvent):
        from os import path
        if self.tipo in ['file', 'path', 'save']:
            self._value = e.path if e.path else None
        if self.tipo == 'file' and e.files:
            self._value = ",".join(map(lambda f: f.path, e.files))
        
        if self._value:
            caminho_pasta, nome_arquivo = path.split(self._value)
            self.text = nome_arquivo[:-4] if self._value else self.nome   
        else:
            self.text = self.nome 
        self.func(self._value)
        self.update()

    def did_mount(self):
        self.page.overlay.append(self.pick_files_dialog)
        self.page.update()

    def will_unmount(self):
        self.page.overlay.remove(self.pick_files_dialog)
        self.page.update()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, valor):
        self._value = valor
        self.text = valor

class Sim(SaveSelectFile2):
    def __init__(self, func,*args, **kwargs):
        super().__init__(nome = 'Sim', tipo = 'save',*args, **kwargs)
        self.func = func
        # self.visible = False
        
    async def save(self, _):
        self.pick_files_dialog.save_file(
            allowed_extensions = ['pkl']
        )

    async def pick_files_result(self, e: ft.FilePickerResultEvent):
        if self.tipo in ['file', 'path', 'save']:
            self._value = e.path if e.path else None
        if self.tipo == 'file' and e.files:
            self._value = ",".join(map(lambda f: f.path, e.files))
        
        self.text = self._value if self._value else self.nome
        if self._value:
            self.func(self._value)
            # print(nome_arquivo,self._value)

        self.update()
        
class SelectorColor2(SelectorColor):
    def __init__(self, control, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.control = control
        self.width = None

        self.adicionados = {}
        self.text_theme_boddy_small = ft.TextStyle(color=None)
        
        self.datas = {
            # "Container": lambda color: setattr(self.color_box, 'bgcolor', color), 
            "Fundo": self.ChangeFundoColor,
            "Texto": lambda color: setattr(self.text_theme, 'color', color),
            "Texto_boddy_small": lambda color: setattr(self.text_theme_boddy_small, 'color', color),

            # "Título": lambda color: setattr(self.titulo, 'color', color),
            # "Texto 1": lambda color: setattr(self.texto1, 'color', color),
            # "Texto 2": lambda color: setattr(self.texto2, 'color', color),
            # "Bordas": self.ChangeBordasColor,
            # "Sombras": self.ChangeSombrasColor,
            "Gradiente": self.ChangeGradienteColor, 
            "Botão": self.ChangeBotao,
            "bgcolor":lambda color: setattr(self.control, 'bgcolor', color),
            "color":lambda color: setattr(self.control, 'color', color),
            # "dropdown_menu_theme":lambda color: setattr(self.page.theme.dropdown_menu_theme.text_style, 'bgcolor', color),
            "primary":  lambda color: setattr(self.color_scheme, 'primary', color),
            "on_primary":  lambda color: setattr(self.color_scheme, 'on_primary', color),
            "on_secondary_container":  lambda color: setattr(self.color_scheme, 'on_secondary_container', color),
            "outline":  lambda color: setattr(self.color_scheme, 'outline', color),
            "shadow":  lambda color: setattr(self.color_scheme, 'shadow', color),
            "on_surface_variant":  lambda color: setattr(self.color_scheme, 'on_surface_variant', color),
            "surface_variant":  lambda color: setattr(self.color_scheme, 'surface_variant', color),
            "primary_container":  lambda color: setattr(self.color_scheme, 'primary_container', color),
            "on_surface":  lambda color: setattr(self.color_scheme, 'on_surface', color),
            "surface":  lambda color: setattr(self.color_scheme, 'surface', color),




            "secondary": lambda color: setattr(self.color_scheme, 'secondary', color),
            "error": lambda color: setattr(self.color_scheme, 'error', color),
            "scrim": lambda color: setattr(self.color_scheme, 'scrim', color),
            "tertiary": lambda color: setattr(self.color_scheme, 'tertiary', color),


            # "secondary_container": lambda color: setattr(self.color_scheme, 'secondary_container', color),
            # "on_secondary_container": lambda color: setattr(self.color_scheme, 'on_secondary_container', color),
            # "on_tertiary": lambda color: setattr(self.color_scheme, 'on_tertiary', color),
            # "tertiary_container": lambda color: setattr(self.color_scheme, 'tertiary_container', color),
            # "on_tertiary_container": lambda color: setattr(self.color_scheme, 'on_tertiary_container', color),
            # "on_error": lambda color: setattr(self.color_scheme, 'on_error', color),
            # "error_container": lambda color: setattr(self.color_scheme, 'error_container', color),
            # "on_error_container": lambda color: setattr(self.color_scheme, 'on_error_container', color),
            # "background": lambda color: setattr(self.color_scheme, 'background', color),
            # "on_background": lambda color: setattr(self.color_scheme, 'on_background', color),
            # "outline_variant": lambda color: setattr(self.color_scheme, 'outline_variant', color),
            # "inverse_surface": lambda color: setattr(self.color_scheme, 'inverse_surface', color),
            # "on_inverse_surface": lambda color: setattr(self.color_scheme, 'on_inverse_surface', color),
            # "inverse_primary": lambda color: setattr(self.color_scheme, 'inverse_primary', color),
            # "surface_tint": lambda color: setattr(self.color_scheme, 'surface_tint', color),
            # "on_primary_fixed": lambda color: setattr(self.color_scheme, 'on_primary_fixed', color),
            # "on_secondary_fixed": lambda color: setattr(self.color_scheme, 'on_secondary_fixed', color),
            # "on_tertiary_fixed": lambda color: setattr(self.color_scheme, 'on_tertiary_fixed', color),
            # "on_primary_fixed_variant": lambda color: setattr(self.color_scheme, 'on_primary_fixed_variant', color),
            # "on_secondary_fixed_variant": lambda color: setattr(self.color_scheme, 'on_secondary_fixed_variant', color),
            # "on_tertiary_fixed_variant": lambda color: setattr(self.color_scheme, 'on_tertiary_fixed_variant', color),
            # "primary_fixed": lambda color: setattr(self.color_scheme, 'primary_fixed', color),
            # "secondary_fixed": lambda color: setattr(self.color_scheme, 'secondary_fixed', color),
            # "tertiary_fixed": lambda color: setattr(self.color_scheme, 'tertiary_fixed', color),
            # "primary_fixed_dim": lambda color: setattr(self.color_scheme, 'primary_fixed_dim', color),
            # "secondary_fixed_dim": lambda color: setattr(self.color_scheme, 'secondary_fixed_dim', color),
            # "surface_bright": lambda color: setattr(self.color_scheme, 'surface_bright', color),
            # "surface_container": lambda color: setattr(self.color_scheme, 'surface_container', color),
            # "surface_container_high": lambda color: setattr(self.color_scheme, 'surface_container_high', color),
            # "surface_container_low": lambda color: setattr(self.color_scheme, 'surface_container_low', color),
            # "surface_container_lowest": lambda color: setattr(self.color_scheme, 'surface_container_lowest', color),
            # "surface_dim": lambda color: setattr(self.color_scheme, 'surface_dim', color),
            # "tertiary_fixed_dim": lambda color: setattr(self.color_scheme, 'tertiary_fixed_dim', color),
            
        }

        self.objetos.options=[ft.dropdown.Option(i) for i in self.datas.keys()]
        self.controles.col =  12
        self.color_box2.col =  12
        self.color_box2.expand =  True
        self.color_box2.height =  None
        self.color_box2.content = self.control
        self.controles.content.controls[0].controls[0].visible = False
        self.controles.content.controls[0].controls[1].visible = False

        self.temas = SaveSelectFile2('file', 'Selecione um arquivo de temas', self.EscolheuTema)
        self.nome_tema_criar = Sim(self.salve)
        self.novo_tema = ft.Container(
            content = ft.Column(
                [
                    ft.Text(f'Deseja criar um novo arquivo de temas?', expand=True, text_align='center'),
                    ft.ResponsiveRow(
                        [
                            self.ContainerHover(
                                self.nome_tema_criar
                            ),
                            
                            self.ContainerHover(
                                ft.FilledButton(
                                    'Não',
                                    bgcolor='grey800',
                                    color="#B0B3B1",                                
                                    on_click=self.SalvarTema
                                    )
                            )
                        ],
                        columns=24,
                        alignment='center',
                    )
                ]
            ),
            visible=False
        )
        self.content = ft.Column(
            controls = [
                ft.ResponsiveRow(
                    controls = [
                        self.caixa(self.color_box2, col = 8),
                        self.caixa(
                            ft.Column(
                                [
                                    self.controles,
  
                                    self.ContainerHover(self.temas),
                                    ft.ResponsiveRow(
                                        [
                                            self.ContainerHover(self.btn_exportar_cores),
                                            self.tema_escolhido], 
                                        alignment='center', 
                                        vertical_alignment='center'                                                      
                                    ),
                                    ft.ResponsiveRow(
                                        [
                                            self.ContainerHover(self.btn_save),
                                            self.nome_tema
                                        ]
                                        , alignment='center',                           
                                    ),
                                    self.novo_tema,                                    
                                    self.tabela_legenda, 
                                    
                                ],
                                
                                scroll=ft.ScrollMode.ADAPTIVE,
                                expand=True,
                            ),
                            col = 4
                        )
                                          
                    ],
                    alignment='center', 
                    columns=12
                
                ),                                                                                                                            
            ], 
            # alignment='center',
            horizontal_alignment='center',
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,  
        )

    def salve(self, caminho = None):
        nome_tema = self.nome_tema.value
        caminho = caminho if caminho else self.nome_temas
        if nome_tema not in ['', ' ', None]:#+list(self.arquiv.keys()):
            print(f'caminho = {caminho}')
            print(f'nome_tema = {nome_tema}')
            self.GetArquivo(caminho)
            self.arquiv[nome_tema] = self.dic
            self.SalvarPickle(self.arquiv, caminho)                                    
            self.tema_escolhido.options.append(ft.dropdown.Option(nome_tema))      
            self.pprint('tema salvo com sucesso!')
        else:
            self.nome_tema.hint_text = 'Digite um nome de Tema válido ou clique em Cancelar'
            # self.nome_tema.hint_style = ft.TextStyle(size = 10)
        self.nome_tema.visible = False
        self.btn_save.visible = True
        self.novo_tema.visible = False
        self.btn_save.update()
        self.novo_tema.update()
        self.tema_escolhido.update()

    def SalvarTema(self, e):
        self.salve()

    def EscolheuTema(self, caminhotema):
        self.GetArquivo(caminhotema)
        self.tema_escolhido.options=[
            ft.dropdown.Option(i) for i in sorted(list(self.arquiv.keys()))
        ]
        self.tema_escolhido.update()
        self.update()
        # print(caminhotema)


    def CriarTema(self, e):
        self.novo_tema.visible = False
        self.nome_tema_criar.visible = True
        self.nome_tema_criar.update()
        self.nome_tema.update()
        self.salve(self.nome_tema_criar.value)

    def Salvar(self, e):
        # print(self.temas.value)
        if self.temas.value:
            self.salve(self.temas.value)

        else:
            self.nome_tema.visible = False
            self.novo_tema.visible = True
            self.novo_tema.update()
            self.nome_tema.update()



        self.update()


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
        def Atibuir(color):
            # setattr(getattr(self.control,atributo), propriedade, color)
            self.set_attrs(self.control, atributo,color)
            # getattr(self.control,atributo).update()
            self.control.update()

        self.datas[nome] = Atibuir
        self.objetos.options=[ft.dropdown.Option(i) for i in self.datas.keys()]
        self.adicionados[nome] = atributo


    def ChangeBotao(self, color):
        self.botao.bgcolor = color
        self.page.theme.elevated_button_theme.bgcolor = color
        self.update()
        self.page.update()
        print('botão')
        # self.SetValueCLienStorage(f'{self.page.title}_Botao', color)
        # self.dic['Botao'] = self.cor

    def caixa(self, control, col = 12):
        return ft.Container(
            padding=15,
            border=ft.border.all(1, 'grey800'),
            border_radius=15,
            col = col,
            content=control,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=60,
                color='#524A76,0.2',
                blur_style = ft.ShadowBlurStyle.OUTER
            )
        )
    def update_color(self, e):
        if e.control.data:
            self.cor = f'#{int(self.slides['r'].value):02X}{int(self.slides['g'].value):02X}{int(self.slides['b'].value):02X}'
            self.datas[e.control.data](self.cor)
            self.update()
            self.page.update()
            # self.SetValueCLienStorage(f'{self.page.title}_{e.control.data}', self.cor)
            self.dic[e.control.data] = self.cor    
            # print(e.control.data, self.dic[e.control.data])    

    def ContainerHover(self, componente):
        def Hover(e):
            if e.data == 'true':
                componente.scale = 1.05
                componente.bgcolor = 'grey700'
                
            else:
                componente.scale = 1
                componente.bgcolor = 'grey800'
                
            componente.update()
        
        return ft.Container(
            content = componente,
            on_hover = Hover,
            col = componente.col
        )



    def ExportarCores(self, e):

        cores =f'''

        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary = "{self.color_scheme.primary}",
                on_primary = "{self.color_scheme.on_primary}",
                on_secondary_container = "{self.color_scheme.on_secondary_container}",
                outline = "{self.color_scheme.outline}",
                shadow = "{self.color_scheme.shadow}",
                on_surface_variant = "{self.color_scheme.on_surface_variant}",
                surface_variant = "{self.color_scheme.surface_variant}",
                primary_container = "{self.color_scheme.primary_container}",
                on_surface = "{self.color_scheme.on_surface}",
                surface = "{self.color_scheme.surface}",
                secondary =" {self.color_scheme.secondary}",
                error = "{self.color_scheme.error}",
                scrim = "{self.color_scheme.scrim}",
                tertiary = "{self.color_scheme.tertiary}"

            ),
            text_theme = ft.TextTheme(
                body_medium=ft.TextStyle(color="{self.text_theme.color}"),  # Cor do texto padrão
                body_small=ft.TextStyle(color="{self.text_theme_boddy_small.color}"),  # Cor do texto padrão
            )   
        ) 
        page.bgcolor =  'surface'   
    '''
        
        for i in self.adicionados.keys():
            self.set_attrs(self.control,self.adicionados[i], self.dic.get(i, self.cor))
            # print(f'{i} = {self.dic.get(i)}')
            cores += f'        self.{self.adicionados[i]} = "{self.dic.get(i)}"\n'

        self.page.set_clipboard(cores)

  
    def CarregarTema(self, e):
        tema = self.tema_escolhido.value
        if tema:

            self.dic = self.arquiv[tema].copy()
            self.titulo.color = self.dic.get('Título')
            self.texto1.color = self.dic.get('Texto 1')
            self.texto2.color = self.dic.get('Texto 2')         
            self.color_text.color = self.dic.get('Texto')
            self.color_box.bgcolor = self.dic.get('Container')
            self.color_box2.bgcolor = self.dic.get('Fundo')
            self.botao.bgcolor = self.dic.get('Botão')

            if isinstance(self.dic.get('Gradiente'), list):
                self.dic['Gradiente'] = self.dic.get('Gradiente')[1]
            if not self.dic.get('Fundo'):
                self.color_box2.bgcolor = 'black'
            if not self.dic.get('Gradiente'):                
                self.gradiente.colors = [self.dic.get('Fundo'),'black']
            else:
                self.gradiente.colors = [self.dic.get('Fundo'), self.dic.get('Gradiente')]

            self.sombras.color = self.dic.get('Sombras')
            self.bordas = ft.border.all(1, self.dic.get('Bordas'))
            self.botao.bgcolor = self.dic.get('Botão')
        

            self.ativar_bordas.value = self.dic.get("Ativar Bordas")
            if self.dic.get("Ativar Bordas"):
                self.color_box.border = self.bordas
            else:
                self.color_box.border = None

            self.ativar_sombras.value = self.dic.get("Ativar Sombras")
            if self.dic.get("Ativar Sombras"):
                self.color_box.shadow = self.sombras
            else:
                self.color_box.shadow = None

            self.ativar_gradiente.value = self.dic.get("Ativar Gradiente")
            if self.color_box2.bgcolor == None:
                self.color_box2.bgcolor = 'black'
            if self.dic.get("Ativar Gradiente"):
                self.gradiente.colors[0] = self.color_box2.bgcolor
                setattr(self.color_box2, 'gradient', self.gradiente)
            else:
                setattr(self.color_box2, 'gradient', None)

            if not self.page.theme:
                self.page.theme = ft.Theme(
                    color_scheme=self.color_scheme,
                    text_theme = ft.TextTheme(
                        body_medium=self.text_theme,  # Cor do texto padrão
                        body_small=self.text_theme_boddy_small  
                    ),
                    scrollbar_theme=ft.ScrollbarTheme(
                        thickness = 10,
                        cross_axis_margin = -15,
                        min_thumb_length = 20,
                        track_color = 'grey500',
                        thumb_color = 'grey900',
                    ),
                    elevated_button_theme = ft.ElevatedButtonTheme(
                        bgcolor = self.dic.get('Botão'),
                    )
                )
            else:
                self.page.theme.text_theme.body_small = self.text_theme_boddy_small

            self.color_scheme.primary = self.dic.get("primary")
            self.color_scheme.on_primary = self.dic.get("on_primary")
            self.color_scheme.on_secondary_container = self.dic.get("on_secondary_container")
            self.color_scheme.outline = self.dic.get("outline")
            self.color_scheme.shadow = self.dic.get("shadow")
            self.color_scheme.on_surface_variant = self.dic.get("on_surface_variant")
            self.color_scheme.surface_variant = self.dic.get("surface_variant")
            self.color_scheme.primary_container = self.dic.get("primary_container")
            self.color_scheme.on_surface = self.dic.get("on_surface")
            self.color_scheme.secondary = self.dic.get("secondary")
            self.color_scheme.error = self.dic.get("error")
            self.color_scheme.scrim = self.dic.get("scrim")
            self.color_scheme.tertiary = self.dic.get("tertiary")


            self.color_scheme.surface = self.color_box2.bgcolor
            self.text_theme.color = self.dic.get("Texto")
            self.text_theme_boddy_small.color = self.dic.get("Texto_boddy_small")




            #carrega as cores de objetos adicionados
            for i in self.adicionados.keys():
                self.set_attrs(self.control,self.adicionados[i], self.dic.get(i, self.cor))
                # print(f'{i} = {self.dic.get(i)}')








            self.update()
            self.page.update()


def Iniciar(control):
    def main(page: ft.Page):
        page.title = 'Selector de Cores2'
        page.add(SelectorColor2(control))
    ft.app(target=main)



if __name__ == '__main__':
    Iniciar(ft.TextField(label='teste', value = 'askjdhaklsjhkj'))